import asyncio
import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar, cast

from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying a function if an exception is raised
    Works for both sync and async functions
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs) 
                    return result  
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            "Retry attempt %d/%d for function '%s' after %.2fs delay (error: %s: %s)",
                            attempt + 1,
                            max_retries,
                            func.__name__,
                            current_delay,
                            type(e).__name__,
                            str(e)
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "Retry exhausted for function '%s' after %d attempts (final error: %s: %s)",
                            func.__name__,
                            max_retries + 1,
                            type(e).__name__,
                            str(e)
                        )
            
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry state")
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            "Retry attempt %d/%d for function '%s' after %.2fs delay (error: %s: %s)",
                            attempt + 1,
                            max_retries,
                            func.__name__,
                            current_delay,
                            type(e).__name__,
                            str(e)
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "Retry exhausted for function '%s' after %d attempts (final error: %s: %s)",
                            func.__name__,
                            max_retries + 1,
                            type(e).__name__,
                            str(e)
                        )
            
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry state")
        
        if asyncio.iscoroutinefunction(func):
            return cast(Callable[..., T], async_wrapper)
        return cast(Callable[..., T], sync_wrapper)
    
    return decorator


def measure_time(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to measure and log execution time
    Works for both sync and async functions
    """
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)  
            return result
        finally:
            elapsed = time.perf_counter() - start
            logger.info(
                "Function '%s' executed in %.2f ms",
                func.__name__,
                round(elapsed * 1000, 2)
            )
    
    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start
            logger.info(
                "Function '%s' executed in %.2f ms",
                func.__name__,
                round(elapsed * 1000, 2)
            )
    
    if asyncio.iscoroutinefunction(func):
        return cast(Callable[..., T], async_wrapper)
    return cast(Callable[..., T], sync_wrapper)

