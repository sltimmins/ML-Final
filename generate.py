#@title Import modules

print('Loading needed modules. Please wait...')
import requests # for MuseNet API
import json


from tegridy_tools import TMIDI


# for plotting/listening only
import matplotlib.pyplot as plt
from midi2audio import FluidSynth

# import matplotlib.pyplot as plt
from IPython.display import display, Javascript, HTML, Audio

# os.chdir('/content/')

# full_path_to_custom_MIDI = "/content/tegridy-tools/tegridy-tools/seed2.mid" #@param {type:"string"}
display_this_number_of_tokens = 512 #@param {type:"slider", min:16, max:4096, step:16}


# data = TMIDI.midi2opus(open(full_path_to_custom_MIDI, 'rb').read())


INSTRUMENTS = ["piano", "piano", "piano", "piano", "piano", "piano", "piano", "piano", "piano",
               "piano", "piano", "piano", "piano", "piano",
               "violin", "violin", "cello", "cello", "bass", "bass", "guitar", "guitar",
               "flute", "flute", "clarinet", "clarinet", "trumpet", "trumpet", "harp", "harp"]

TRACK_INDEX = {"piano": 0, "guitar": 1, "bass": 2,  "violin": 3, "cello": 4,  "flute": 5,
               "clarinet": 6, "harp": 7, "trumpet": 8, "drum": 9}

R_TRACK_INDEX = {0: "piano", 1: "guitar", 2: "bass", 3: "violin", 4: "cello", 5: "flute",
               6: "clarinet", 7: "harp", 8: "trumpet", 9: "drum"}


VOLUMES = [0, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 80, 0, 80, 0, 80, 0, 80, 0, 80,
           0, 80, 0, 80, 0, 80, 0, 100]


def generate_song(instruments, genre):

    use_loaded_custom_MIDI = True
    trim_custom_MIDI_tokens = 512


    #@markdown Generation settings
    number_of_tokens_to_generate = 512 #@param {type:"slider", min:64, max:1024, step:8}

    # if use_loaded_custom_MIDI and len(encoded) > 16:
    #     c_encoding = ' '.join([str(y) for y in encoded[:trim_custom_MIDI_tokens]])
    # else:
    c_encoding = ''

    headers = {"Content-Type": "application/json"}

    data = json.dumps({
            
                "genre": genre,

                "instrument":instruments,

                "encoding": c_encoding,

                "temperature": 1,

                "truncation": 0,

                "generationLength": number_of_tokens_to_generate,

                "audioFormat": "audio/ogg"})

    response = requests.post('https://musenet.openai.com/sample', headers=headers, data=data)

    print('Decoding...')
    res = response.json()

    encoding = [int(y) for y in res['completions'][0]['encoding'].split()]

    print('Done!')

    song = []
    delta_times = 0
    for token in encoding:
        if 0 <= int(token) < 3840:
            note = int(token) % 128
            inst_vol_index = (int(token) // 128) 
            velocity = VOLUMES[inst_vol_index]
            channel = TRACK_INDEX[INSTRUMENTS[inst_vol_index]]
            delay = delta_times
            if velocity > 0:
                song.append(['note_on', delay * 20, channel, note, velocity])

            else:
                song.append(['note_off', delay * 20, channel, note, velocity])

            
        elif 3840 <= int(token) < 3968:
            note = int(token) % 128
            inst_vol_index = (int(token) // 128)
            velocity = 100
            channel = 9 
            delay = delta_times

            song.append(['note_on', delay* 20, channel, note, velocity])



            song.append(['note_off', delay+1 * 20, channel, note, 0])


        elif 3968 <= int(token) < 4096:
            delta_times = (int(token) % 128)
            
        elif int(token) == 4096:
            pass
                #return {"type": "start"}
        else:
            pass


    output_signature = 'MuseNet Companion'
    track_name = 'Project Los Angeles'
    number_of_ticks_per_quarter = 1000
    list_of_MIDI_patches = [0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 0, 0, 0, 0, 0, 0]
    text_encoding='ISO-8859-1'


    output_header = [number_of_ticks_per_quarter, 
                        [['track_name', 0, bytes(output_signature, text_encoding)]]]                                                    

    patch_list = [['patch_change', 0, 0, list_of_MIDI_patches[0]], 
                        ['patch_change', 0, 1, list_of_MIDI_patches[1]],
                        ['patch_change', 0, 2, list_of_MIDI_patches[2]],
                        ['patch_change', 0, 3, list_of_MIDI_patches[3]],
                        ['patch_change', 0, 4, list_of_MIDI_patches[4]],
                        ['patch_change', 0, 5, list_of_MIDI_patches[5]],
                        ['patch_change', 0, 6, list_of_MIDI_patches[6]],
                        ['patch_change', 0, 7, list_of_MIDI_patches[7]],
                        ['patch_change', 0, 8, list_of_MIDI_patches[8]],
                        ['patch_change', 0, 9, list_of_MIDI_patches[9]],
                        ['patch_change', 0, 10, list_of_MIDI_patches[10]],
                        ['patch_change', 0, 11, list_of_MIDI_patches[11]],
                        ['patch_change', 0, 12, list_of_MIDI_patches[12]],
                        ['patch_change', 0, 13, list_of_MIDI_patches[13]],
                        ['patch_change', 0, 14, list_of_MIDI_patches[14]],
                        ['patch_change', 0, 15, list_of_MIDI_patches[15]],
                        ['track_name', 0, bytes(track_name, text_encoding)]]

    output = output_header + [patch_list + song]

    midi_data = TMIDI.opus2midi(output, text_encoding)

    with open('bin/song.mid', 'wb') as midi_file:
        midi_file.write(midi_data)
        midi_file.close()


    FluidSynth("bin/FluidR3_GM.sf2", 16000).midi_to_audio('bin/song.mid', 'bin/song.wav')
    Audio('bin/song.wav', rate=16000)

    return './bin/song.wav'