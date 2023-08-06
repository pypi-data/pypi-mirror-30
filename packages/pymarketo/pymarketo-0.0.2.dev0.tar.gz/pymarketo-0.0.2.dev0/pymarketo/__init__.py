from marketorestpython.client import MarketoClient
import os

class Marketo(MarketoClient):
    def __init__(self, client_server, client_id, client_secret):
        super().__init__(client_server, client_id, client_secret)
    
    # --------- BULK EXTRACT LEADS & ACTIVITIES ---------
    # NOTE: THIS IS PART OF A PULL REQUEST TO THE MARKETORESTPYTHON PROJECT AND WILL BE REMOVED ONCE MERGED 

    def _get_export_jobs_list(self, entity):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + f'/bulk/v1/{entity}/export.json', args)
        if not result['success']:
            raise MarketoException(result['errors'][0])
        return result['result']

    def _create_bulk_export_job(self, entity, fields, filters, format='CSV', columnHeaderNames=None):
        assert entity is not None, 'Invalid argument: required fields is none.'
        assert fields is not None, 'Invalid argument: required fields is none.'
        assert filters is not None, 'Invalid argument: required filters is none.'
        data = {'fields': fields, 'format': format, 'filter': filters}
        if columnHeaderNames is not None:
            data['columnHeaderNames'] = columnHeaderNames
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + f'/bulk/v1/{entity}/export/create.json', args, data)
        if not result['success']:
            raise MarketoException(result['errors'][0])
        return result['result']

    def _export_job_state_machine(self, entity, state, job_id):
        assert entity is not None, 'Invalid argument: required fields is none.'
        assert entity is not None, 'Invalid argument: required fields is none.'
        assert job_id is not None, 'Invalid argument: required fields is none.'
        state_info = {'enqueue': {'suffix': '/enqueue.json', 'method': 'post'}, 'cancel': {
            'suffix': '/cancel.json', 'method': 'post'}, 'status': {'suffix': '/status.json', 'method': 'get'}, 'file': {'suffix': '/file.json', 'method': 'get'}}
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            state_info[state]['method'], self.host + f'/bulk/v1/{entity}/export/{job_id}'+state_info[state]['suffix'], args, mode='nojson')
        if state is 'file' and result.status_code is 200:
            return result.content
        if not result['success']:
            raise MarketoException(result['errors'][0])
        return result['result']

    def get_leads_export_job_file(self, *args, **kargs):
        return self._export_job_state_machine('leads', 'file', *args, **kargs)

    def get_activities_export_job_file(self, *args, **kargs):
        return self._export_job_state_machine('activities', 'file', *args, **kargs)

    def get_leads_export_job_status(self, *args, **kargs):
        return self._export_job_state_machine('leads', 'status', *args, **kargs)

    def get_activities_export_job_status(self, *args, **kargs):
        return self._export_job_state_machine('activities', 'status', *args, **kargs)

    def cancel_leads_export_job(self, *args, **kargs):
        return self._export_job_state_machine('leads', 'cancel', *args, **kargs)

    def cancel_activities_export_job(self, *args, **kargs):
        return self._export_job_state_machine('activities', 'cancel', *args, **kargs)

    def enqueue_leads_export_job(self, *args, **kargs):
        return self._export_job_state_machine('leads', 'enqueue', *args, **kargs)

    def enqueue_activities_export_job(self, *args, **kargs):
        return self._export_job_state_machine('activities', 'enqueue', *args, **kargs)

    def create_leads_export_job(self, *args, **kargs):
        return self._create_bulk_export_job('leads', *args, **kargs)

    def create_activities_export_job(self, *args, **kargs):
        return self._create_bulk_export_job('activities', *args, **kargs)

    def get_leads_export_jobs_list(self):
        return self._get_export_jobs_list('leads')

    def get_activities_export_jobs_list(self):
        return self._get_export_jobs_list('activities')



# def main():
#     mkto = Marketo(os.getenv('MKTO_CLIENT_SERVER'), os.getenv('MKTO_CLIENT_ID'), os.getenv('MKTO_CLIENT_SECRET'))



# if __name__ == '__main__':
#     main()