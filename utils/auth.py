#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Google Cloud Platform authentication and environment resolution utilities.
#       Validates Application Default Credentials (ADC) and extracts active GCP project IDs.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 14/08/2024          Saddam Khan        Initial implementation
# 10/09/2024          Saddam Khan        Enhanced GCP project and ADC credential resolution
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import google.auth
from google.auth.exceptions import DefaultCredentialsError

def resolve_gcp_project(configured_project: str = "") -> str:
    """
    Explanation: Resolves GCP project ID by evaluating explicit config, environment variables, and ADC
    :param  configured_project str: User-specified GCP project identifier
    :return project_id str: Validated GCP project ID or empty string if unresolved
    """
    if configured_project and configured_project.strip():
        return configured_project.strip()

    env_project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT")
    if env_project and env_project.strip():
        return env_project.strip()

    try:
        credentials, project_id = google.auth.default()
        if project_id:
            return project_id
    except DefaultCredentialsError:
        pass

    return ""

def verify_adc() -> tuple[bool, str]:
    """
    Explanation: Verifies whether Google Application Default Credentials (ADC) are valid and accessible
    :return is_valid bool: Flag indicating whether ADC authentication succeeded
    :return details str: Discovered project ID or descriptive error message
    """
    try:
        credentials, project_id = google.auth.default()
        return True, project_id or ""
    except DefaultCredentialsError as e:
        return False, str(e)
