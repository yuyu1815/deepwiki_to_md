"""
統一エラーハンドリングシステム

プロジェクト全体で使用される統一されたエラーハンドリング、
再試行戦略、ログ管理を提供するモジュール。
"""

import time
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, Callable, Dict, List
from dataclasses import dataclass
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError


class ErrorType(Enum):
    """エラー種別"""
    NETWORK_ERROR = "network_error"
    PARSE_ERROR = "parse_error"
    VALIDATION_ERROR = "validation_error"
    CONTENT_ERROR = "content_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class HandleResult:
    """エラーハンドリング結果"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    final_attempt: bool = True


class RetryStrategy(ABC):
    """再試行戦略の抽象基底クラス"""
    
    @abstractmethod
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """再試行すべきかどうかを判定"""
        pass
    
    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """再試行前の待機時間を取得"""
        pass
    
    @abstractmethod
    def get_max_attempts(self) -> int:
        """最大試行回数を取得"""
        pass


class ExponentialBackoffRetry(RetryStrategy):
    """指数バックオフ再試行戦略"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """ネットワークエラーの場合のみ再試行"""
        if attempt >= self.max_attempts:
            return False
        
        return isinstance(error, (RequestException, ConnectionError, Timeout))
    
    def get_delay(self, attempt: int) -> float:
        """指数的に増加する待機時間"""
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)
    
    def get_max_attempts(self) -> int:
        return self.max_attempts


class LinearRetry(RetryStrategy):
    """線形再試行戦略"""
    
    def __init__(self, max_attempts: int = 2, delay: float = 1.0):
        self.max_attempts = max_attempts
        self.delay = delay
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        return attempt < self.max_attempts
    
    def get_delay(self, attempt: int) -> float:
        return self.delay
    
    def get_max_attempts(self) -> int:
        return self.max_attempts


class ImmediateFailure(RetryStrategy):
    """即座に失敗する戦略（再試行なし）"""
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        return False
    
    def get_delay(self, attempt: int) -> float:
        return 0.0
    
    def get_max_attempts(self) -> int:
        return 1


class SingleRetryWithFallback(RetryStrategy):
    """一度だけ再試行する戦略"""
    
    def __init__(self, delay: float = 0.5):
        self.delay = delay
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        return attempt < 2
    
    def get_delay(self, attempt: int) -> float:
        return self.delay
    
    def get_max_attempts(self) -> int:
        return 2


class UnifiedErrorHandler:
    """統一されたエラーハンドリングシステム"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初期化
        
        Args:
            logger: ログ出力用のLogger（Noneの場合はデフォルトを作成）
        """
        self.logger = logger or self._create_default_logger()
        
        # エラー種別ごとの再試行戦略
        self.retry_strategies: Dict[ErrorType, RetryStrategy] = {
            ErrorType.NETWORK_ERROR: ExponentialBackoffRetry(max_attempts=3),
            ErrorType.PARSE_ERROR: ImmediateFailure(),
            ErrorType.VALIDATION_ERROR: SingleRetryWithFallback(),
            ErrorType.CONTENT_ERROR: LinearRetry(max_attempts=2),
            ErrorType.UNKNOWN_ERROR: LinearRetry(max_attempts=2)
        }
    
    def _create_default_logger(self) -> logging.Logger:
        """デフォルトロガーの作成"""
        logger = logging.getLogger('deepwiki_to_md')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def handle_with_retry(
        self, 
        operation: Callable[[], Any], 
        context: str,
        error_classifier: Optional[Callable[[Exception], ErrorType]] = None
    ) -> HandleResult:
        """
        操作を実行し、エラーが発生した場合は再試行戦略に従って処理
        
        Args:
            operation: 実行する操作
            context: エラー発生時のコンテキスト情報
            error_classifier: エラー分類関数（Noneの場合はデフォルト分類を使用）
            
        Returns:
            HandleResult: 実行結果
        """
        classifier = error_classifier or self._default_error_classifier
        last_error = None
        
        for attempt in range(10):  # 最大試行回数の上限
            try:
                result = operation()
                
                if attempt > 0:
                    self.logger.info(f"操作成功（試行回数: {attempt + 1}）: {context}")
                
                return HandleResult(
                    success=True,
                    result=result,
                    retry_count=attempt,
                    final_attempt=True
                )
                
            except Exception as error:
                last_error = error
                error_type = classifier(error)
                strategy = self.retry_strategies.get(error_type, self.retry_strategies[ErrorType.UNKNOWN_ERROR])
                
                self.logger.warning(
                    f"エラー発生（試行 {attempt + 1}）: {context} - {error_type.value}: {str(error)}"
                )
                
                if not strategy.should_retry(error, attempt):
                    self.logger.error(f"再試行中止: {context} - 最終エラー: {str(error)}")
                    break
                
                # 再試行前の待機
                delay = strategy.get_delay(attempt)
                if delay > 0:
                    self.logger.info(f"再試行前に {delay}秒 待機中...")
                    time.sleep(delay)
        
        return HandleResult(
            success=False,
            error=str(last_error),
            retry_count=attempt + 1,
            final_attempt=True
        )
    
    def _default_error_classifier(self, error: Exception) -> ErrorType:
        """デフォルトのエラー分類器"""
        if isinstance(error, (RequestException, ConnectionError, Timeout)):
            return ErrorType.NETWORK_ERROR
        elif isinstance(error, (ValueError, TypeError, KeyError)):
            return ErrorType.PARSE_ERROR
        elif isinstance(error, AssertionError):
            return ErrorType.VALIDATION_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def log_error(self, error: Exception, context: str, additional_info: Optional[Dict[str, Any]] = None):
        """
        エラーをログに記録
        
        Args:
            error: 発生したエラー
            context: エラーのコンテキスト
            additional_info: 追加情報
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        if additional_info:
            error_info.update(additional_info)
        
        self.logger.error(f"エラー詳細: {error_info}")
    
    def log_success(self, context: str, additional_info: Optional[Dict[str, Any]] = None):
        """
        成功をログに記録
        
        Args:
            context: 成功したコンテキスト
            additional_info: 追加情報
        """
        success_info = {'context': context}
        
        if additional_info:
            success_info.update(additional_info)
        
        self.logger.info(f"操作成功: {success_info}")
    
    def set_retry_strategy(self, error_type: ErrorType, strategy: RetryStrategy):
        """
        特定のエラー種別に対する再試行戦略を設定
        
        Args:
            error_type: エラー種別
            strategy: 再試行戦略
        """
        self.retry_strategies[error_type] = strategy
        self.logger.info(f"再試行戦略を更新: {error_type.value} -> {type(strategy).__name__}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        エラー統計情報を取得（実装は将来の拡張用）
        
        Returns:
            dict: エラー統計情報
        """
        # 将来的にエラー統計を追跡する場合の拡張ポイント
        return {
            'total_errors': 0,
            'error_types': {},
            'retry_statistics': {}
        }


class ContentValidationError(Exception):
    """コンテンツ検証エラー"""
    def __init__(self, message: str, validation_details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.validation_details = validation_details or {}


class ExtractionError(Exception):
    """データ抽出エラー"""
    def __init__(self, message: str, url: Optional[str] = None, extraction_step: Optional[str] = None):
        super().__init__(message)
        self.url = url
        self.extraction_step = extraction_step


class ConfigurationError(Exception):
    """設定エラー"""
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key


# 便利関数
def create_error_handler(log_level: str = "INFO") -> UnifiedErrorHandler:
    """
    エラーハンドラーを作成する便利関数
    
    Args:
        log_level: ログレベル
        
    Returns:
        UnifiedErrorHandler: エラーハンドラーインスタンス
    """
    logger = logging.getLogger('deepwiki_to_md')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    return UnifiedErrorHandler(logger)


def safe_execute(
    operation: Callable[[], Any], 
    context: str,
    error_handler: Optional[UnifiedErrorHandler] = None,
    default_return: Any = None
) -> Any:
    """
    安全に操作を実行する便利関数
    
    Args:
        operation: 実行する操作
        context: エラー発生時のコンテキスト
        error_handler: エラーハンドラー（Noneの場合はデフォルトを作成）
        default_return: エラー時のデフォルト戻り値
        
    Returns:
        Any: 操作の結果またはデフォルト値
    """
    handler = error_handler or create_error_handler()
    
    result = handler.handle_with_retry(operation, context)
    
    if result.success:
        return result.result
    else:
        handler.logger.warning(f"操作失敗、デフォルト値を返します: {context}")
        return default_return