import whisper
import os
from datetime import timedelta
import re

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def is_sentence_end(word):
    return word.strip().endswith(('.', '!', '?'))

def transcribe_audio(input_file, output_file, output_directory, max_words_per_line, language, model_name, prompt, pause_threshold):
    model = whisper.load_model(model_name)
    result = model.transcribe(input_file, language=language, initial_prompt=prompt, word_timestamps=True)
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    output_path = os.path.join(output_directory, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        subtitle_index = 1
        words = []
        start_time = None
        prev_end_time = 0
        
        for segment in result['segments']:
            for word in segment['words']:
                if start_time is None:
                    start_time = word['start']
                
                # Check for long pause or sentence end
                if (word['start'] - prev_end_time > pause_threshold) or (words and is_sentence_end(words[-1]['word'])):
                    if words:
                        end_time = prev_end_time
                        text = ' '.join(w['word'] for w in words)
                        text = re.sub(r'\s+', ' ', text.strip())
                        
                        f.write(f"{subtitle_index}\n")
                        f.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
                        f.write(f"{text}\n\n")
                        
                        subtitle_index += 1
                        words = []
                        start_time = word['start']
                
                words.append(word)
                if len(words) == max_words_per_line or is_sentence_end(word['word']):
                    end_time = word['end']
                    text = ' '.join(w['word'] for w in words)
                    text = re.sub(r'\s+', ' ', text.strip())
                    
                    f.write(f"{subtitle_index}\n")
                    f.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
                    f.write(f"{text}\n\n")
                    
                    subtitle_index += 1
                    words = []
                    start_time = None
                
                prev_end_time = word['end']
        
        # Write any remaining words
        if words:
            end_time = words[-1]['end']
            text = ' '.join(w['word'] for w in words)
            text = re.sub(r'\s+', ' ', text.strip())
            
            f.write(f"{subtitle_index}\n")
            f.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
            f.write(f"{text}\n\n")
    
    print(f"Transcription saved to: {output_path}")

if __name__ == "__main__":
    input_file = input("Enter the path to the input audio/video file: ").strip('\"')
    output_directory = input("Enter the output directory: ").strip('\"')
    output_file = input("Enter the desired output file name (with extension, e.g., output.srt): ").strip('\"')

    # Hardcoded parameters
    max_words_per_line = 3
    language = "en"
    model_name = "medium"
    prompt = "words in video may be cyde.xyz,auto crystal, auto totem, click crystals, anchor macro, fastEXP, middle click pearl, %appdata%"
    pause_threshold = 1.0

    transcribe_audio(
        input_file=input_file,
        output_file=output_file,
        output_directory=output_directory,
        max_words_per_line=max_words_per_line,
        language=language,
        model_name=model_name,
        prompt=prompt,
        pause_threshold=pause_threshold
    )
