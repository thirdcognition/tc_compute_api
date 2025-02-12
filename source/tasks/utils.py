from app.core.celery_app import celery_app


@celery_app.task
def collect_results(results):
    """
    Collect results from parallel tasks.

    :param results: List of results from executed tasks.
    :return: Filtered list of successful results.
    """
    return [result for result in results if result]
