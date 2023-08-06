import json

from pymkv import MKVFile, MKVTrack, Timestamp, MKVAttachment
from bitmath import *
import pickle


# mkv = MKVFile()
# mkv.add_track('/Users/sheldonwoodward/Movies/pymkv-test-project/tracks/video.h264')
# mkv.add_track('/Users/sheldonwoodward/Movies/pymkv-test-project/tracks/audio.aac')
# mkv.add_chapters('/Users/sheldonwoodward/Movies/pymkv-test-project/chapters/chapters.xml', 'und')
# mkv.mux('/Users/sheldonwoodward/Desktop/test.mkv')
# mkv.add_file('~/Movies/pymkv-test-project/sample.mkv')
# print(mkv.command('~/Movies/pymkv-test-project/output.mkv'))
# print(mkv.get_json('/Users/sheldonwoodward/Desktop/test.mkv'))

# mkv1 = MKVFile('/Users/sheldonwoodward/Movies/pymkv-test-project/output-chaptered.mkv')
# mkv2 = MKVFile('/Users/sheldonwoodward/Movies/pymkv-test-project/output-X-chaptered.mkv')
# mkv1.add_file(mkv2)
# mkv1.add_chapters('/Users/sheldonwoodward/Movies/pymkv-test-project/chapters/chapters3.txt')
# mkv1.mux('/Users/sheldonwoodward/Movies/pymkv-test-project/output.mkv')

# track = MKVTrack('/Users/sheldonwoodward/Movies/pymkv-test-project/tracks/video.h264')
# mkv = MKVFile('/Users/sheldonwoodward/Movies/pymkv-test-project/output-chaptered.mkv')
# mkv.exclude_internal_chapters()
# mkv.add_chapters('/Users/sheldonwoodward/Movies/pymkv-test-project/chapters/chapters2.txt')
# mkv.mux('/Users/sheldonwoodward/Movies/pymkv-test-project/output.mkv')
# print(mkv.get_track(0))

# mkv = MKVFile('~/Movies/pymkv-test-project/sample.mkv')
# mkv.split_duration(10)
# mkv.link_to_next('~/Desktop/test-002.mkv')
# mkv.add_chapters('~/Movies/pymkv-test-project/chapters/chapters.txt')
# mkv.split_timestamps(1, 2, 3, 4)
# mkv.split_timestamp_parts(((None, '00:01', '00:02', 3), (4, 5), (6, None)))
# mkv.split_parts_frames(((10, 20, 30, 40), (50, None)))
# mkv.split_frames(10, 20, 30, (40, 50, (60, 70), 80, 90), 100)
# mkv.split_chapters(2)
# mkv.mux('~/Movies/pymkv-test-project/output.mkv')

# mkv = MKVFile('~/Movies/pymkv-test-project/output.mkv')
# mkv.track_tags(0, exclusive=False)
# mkv.no_global_tags()
# mkv.global_tags('~/Movies/pymkv-test-project/tags/tags.xml')
# mkv.mux('~/Movies/pymkv-test-project/output2.mkv')

mkv = MKVFile('~/Movies/pymkv-test-project/sample.mkv')
mkv.add_attachment(MKVAttachment('~/Movies/pymkv-test-project/attachments/attachment.jpg', name="A1"))
mkv.add_attachment(MKVAttachment('~/Movies/pymkv-test-project/attachments/attachment.jpg', name="A2"))
mkv.mux('~/Movies/pymkv-test-project/output.mkv')

# p = pickle.dumps(mkv)
# print(p)
# mkv2 = pickle.loads(p)
# print(mkv2.__dict__)