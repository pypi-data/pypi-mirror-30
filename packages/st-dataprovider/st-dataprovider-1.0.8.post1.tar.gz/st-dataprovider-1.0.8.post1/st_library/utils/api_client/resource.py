from urlobject import URLObject


ROOT = URLObject('https://shortesttrack.com')

METADATA_ENDPOINT = ROOT.add_path('api/metadata/')
EXECUTION_METADATA_ENDPOINT = ROOT.add_path('api/execution-metadata/')
LOGGING_ENDPOINT = ROOT.add_path('api/logging/')
DATA_ENDPOINT = ROOT.add_path('api/data')


PERFORMANCES_LIST_GET_PATH = EXECUTION_METADATA_ENDPOINT.add_path('v2/performances/')


def sec_get_detail(uuid):
    return METADATA_ENDPOINT.add_path('script-execution-configurations/{uuid}'.format(uuid=uuid))


def performance_get_detail(uuid):
    return EXECUTION_METADATA_ENDPOINT.add_path('v2/performances/{uuid}/'.format(uuid=uuid))


def performance_output_parameter_post(parameter_id, performance_id):
    return EXECUTION_METADATA_ENDPOINT.\
        add_path('v2/performances/{performance_id}/output-parameters/{parameter_id}/value/'.
                 format(performance_id=performance_id, parameter_id=parameter_id))


def logging_post(performance_id):
    return LOGGING_ENDPOINT.add_path('performances/{performance_id}/'.format(performance_id=performance_id))


def matrices(matrices_id):
    return METADATA_ENDPOINT.add_path('matrices/{matrices_id}'.format(matrices_id=matrices_id))


def matrices_upload(dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('datasets/{dataset_id}/matrices/{matrices_id}/upload'.
                                  format(dataset_id=dataset_id, matrices_id=matrices_id))


def matrices_get(dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('datasets/{dataset_id}/matrices/{matrices_id}/data'.
                                  format(dataset_id=dataset_id, matrices_id=matrices_id))


def sec_matrices_get(sec_id, dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/datasets/'
                                  '{dataset_id}/matrices/{matrices_id}/data'.
                                  format(sec_id=sec_id, dataset_id=dataset_id, matrices_id=matrices_id))


def sec_matrices_insert(sec_id, dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/datasets/'
                                  '{dataset_id}/matrices/{matrices_id}/insert'.
                                  format(sec_id=sec_id, dataset_id=dataset_id, matrices_id=matrices_id))


def sec_matrices_batch_insert(sec_id, dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/datasets/'
                                  '{dataset_id}/matrices/{matrices_id}/upload'.
                                  format(sec_id=sec_id, dataset_id=dataset_id, matrices_id=matrices_id))


def object_download(repo_id, file_id):
    return DATA_ENDPOINT.add_path('blob-repositories/{repo_id}/download'.
                                  format(repo_id=repo_id)).add_query_param('name', file_id)


def object(repo_id, file_id):
    return DATA_ENDPOINT.add_path('blob-repositories/{repo_id}'.
                                  format(repo_id=repo_id)).add_query_param('name', file_id)
