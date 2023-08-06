from marketorestpython.client import MarketoClient
from itertools import chain
import os


class Marketo(MarketoClient):
    def __init__(self, munchkin_id, client_id, client_secret):
        super().__init__(client_server, client_id, client_secret)

    def get_all_segments(self):
        results = list()
        segmentations = self.get_segmentations()
        all_segments = list(chain.from_iterable(
            map((lambda s: self.get_segments(s['id'])), segmentations)))
        return all_segments

    def get_all_programs(self):
        results = list()
        programs = self.browse_programs()
        all_programs = list(chain.from_iterable(
            map((lambda p: self.get_program_by_id(p['id'])), programs)))
        return all_programs

# def main():
#     mkto = Marketo(os.getenv('MKTO_CLIENT_SERVER'), os.getenv('MKTO_CLIENT_ID'), os.getenv('MKTO_CLIENT_SECRET'))
#     # print(len(mkto.get_multiple_campaigns()))
#     # print(len(mkto.get_all_segments()))
#     # print(mkto.get_all_programs())
#     # print(len(mkto.get_activity_types()))


# if __name__ == '__main__':
#     main()
