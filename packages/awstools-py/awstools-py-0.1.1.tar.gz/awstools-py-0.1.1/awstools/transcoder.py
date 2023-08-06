from vital.cache import cached_property

from awstools._aws import AwsManager
from awstools.utils import unpythonize


__all__ = (
    'TranscoderManager',
    'TranscoderOutput',
    'HlsOutput',
    'HlsAudioOutput',
    'DashOutput',
    'DashAudioOutput',
    'TranscoderPlaylist',
    'TranscoderClip',
    'HlsPlaylist',
    'HlsV4Playlist',
    'DashPlaylist')


class TranscoderManager(AwsManager):
    CLIENT_NAME = 'elastictranscoder'

    def __init__(self, pipeline_id, outputs=None, playlists=None, **kwargs):
        super(TranscoderManager, self).__init__(**kwargs)
        self.pipeline_id = pipeline_id
        self.outputs = list(outputs or [])
        self.playlists = playlists or []

    def create(self, fn):
        return self.client.create_job(PipelineId=self.pipeline_id,
                                      Input={'Key': fn},
                                      Outputs=self.outputs,
                                      Playlists=self.playlists)

    def cancel(self, job_id):
        return self.client.cancel_job(Id=job_id)

    def read(self, job_id):
        return self.client.read_job(Id=job_id)


class TranscoderOutput(dict):

    def __init__(self, name, preset_id, key=None, rotate='auto',
                 extension=None, **opt):
        opt = unpythonize(opt)
        if opt.get('SegmentDuration') is not None:
            opt['SegmentDuration'] = str(opt['SegmentDuration'])
        super(TranscoderOutput, self).__init__(PresetId=preset_id,
                                               Key=key,
                                               **opt)
        self.name = name
        self.extension = extension.lstrip('.') if extension else extension

    @property
    def key(self):
        return self['Key']

    def set_thumb_pattern(self, pattern=None):
        self['ThumbnailPattern'] = pattern or self.generate_thumb_pattern()

    def generate_thumb_pattern(self):
        key = self['Key']
        key = key.split('/')
        key = '%s/%s%s' % ('/'.join(key[:-1]), 'thumbs/', key[-1])
        parts = list(key.split('.')[:-1])
        parts.append('{count}')
        return '.'.join(parts)

    def set_key(self, key):
        self['Key'] = key

    def generate_key(self, input_key):
        parts = input_key.split('.')
        ext = parts[-1]
        parts = list(parts[:-1])
        parts.append(self.name)
        parts.append(self.extension or ext)
        return '.'.join(filter(len, parts))



class DashOutput(TranscoderOutput):

    def __init__(self, name, preset_id, segment_duration=3.0, **kwargs):
        super(DashOutput, self).__init__(
            name, preset_id, segment_duration=segment_duration,
            extension='dash', **kwargs)


class DashAudioOutput(TranscoderOutput):

    def __init__(self, name, preset_id, segment_duration=3.0, **kwargs):
        super(DashAudioOutput, self).__init__(
            name, preset_id, segment_duration=segment_duration,
            extension='audio.dash', **kwargs)


class HlsOutput(TranscoderOutput):

    def __init__(self, name, preset_id, segment_duration=3.0, **kwargs):
        super(HlsOutput, self).__init__(
            name, preset_id, segment_duration=segment_duration, **kwargs)

    def generate_key(self, input_key):
        parts = input_key.split('.')
        ext = parts[-1]
        parts = list(parts[:-1])
        parts.append(self.name)
        return '.'.join(filter(len, parts)) + '-'


class HlsAudioOutput(HlsOutput):

    def __init__(self, name, preset_id, segment_duration=3.0, **kwargs):
        super(HlsAudioOutput, self).__init__(
            name, preset_id, segment_duration=segment_duration,
            extension='audio', **kwargs)


class TranscoderClip(dict):
    def __init__(self, start_time, duration, max_duration=-1):
        """ @start_time: (#float)
            @duration: (#float)
        """
        if max_duration > -1 and duration > max_duration:
            raise ValueError("Duration cannot be greater than %s" %
                             max_duration)
        super(TranscoderClip, self).__init__(
            TimeSpan=dict(StartTime=start_time, Duration=duration))


class TranscoderPlaylist(dict):
    '''
    "Playlists":[
      {
         "Format":"HLSv3|HLSv4|MPEG-DASH|Smooth",
         "Name":"name",
         "OutputKeys":[
            "Outputs:Key to include in this playlist",
            ...
         ],
      }
    ]
    '''
    HLS = 'HLSv3'
    HLS_V3 = HLS
    HLS_V4 = 'HLSv4'
    DASH = 'MPEG-DASH'
    SMOOTH = 'Smooth'

    def __init__(self, name, format, outputs, drm=None):
        """ @name: (#str) name of the playlist
            @format: (#str) 'HLSv3', 'HLSv4', 'MPEG-DASH', 'Smooth'
            @*outputs: (:class:TranscoderOutput) output keys
                to add to the playlist, in the order they should appear
        """
        super(TranscoderPlaylist, self).__init__(
            Format=format, Name=name,
            OutputKeys=[output.key for output in outputs])

    def set_name(self, name):
        self['Name'] = name

    def add(self, *outputs):
        """ Adds an output to the playlist """
        self.OutputKeys.extend(output.key for output in outputs)

    def protect(self, drm):
        """ Adds a DRM configuration """


class HlsPlaylist(TranscoderPlaylist):

    def __init__(self, name, outputs, **kwargs):
        super(HlsPlaylist, self).__init__(name, self.HLS, outputs, **kwargs)


class HlsV4Playlist(TranscoderPlaylist):

    def __init__(self, name, outputs, **kwargs):
        super(HlsV4Playlist, self).__init__(
            name, self.HLS_V4, outputs, **kwargs)


class DashPlaylist(TranscoderPlaylist):

    def __init__(self, name, outputs, **kwargs):
        super(DashPlaylist, self).__init__(name, self.DASH, outputs, **kwargs)
