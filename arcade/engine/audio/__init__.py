
import bpy, os, aud


class Audio_Player:

    def __init__(self):
        self.audio_files = {}
        self.device = aud.Device()
    

    def load_audio_files(self, audio_files=[]):
        '''Load a list of audio files\n
        Params: audio_files = ["name.mp3", "name.mp3"]'''

        if audio_files != []:

            for audio_file in audio_files:

                # Could not load the file : Reset audio files
                if not self.__load_audio(audio_file):
                    self.audio_files = {}
                    return None

                sound = self.__load_audio(audio_file)

                # Save the audio
                if audio_file not in self.audio_files:
                    self.audio_files[audio_file] = sound


    def play_audio(self, audio_file):
        '''Play an audio clip.'''

        if audio_file in self.audio_files:
            self.device.play(self.audio_files[audio_file])


    def __load_audio(self, audio_file):
        '''Load the audio file into memory.'''

        aud_path = os.path.abspath(os.path.join(os.path.dirname(__file__), audio_file))

        # Check if the audio is supported by blender
        type = F'.{aud_path.split(".")[-1]}'
        if type not in bpy.path.extensions_audio:
            print(F'Unable to play audio with this blender build: {type}')
            return None

        audio_track = aud.Sound(aud_path)
        audio_track = audio_track.resample(10000, False)
        audio_track = audio_track.cache()
        return audio_track

    