import wave
import os
import numpy as np

# Open audio file
wf = wave.open("input.wav", "rb")

frame_rate = wf.getframerate()
n_frames = wf.getnframes()

audio_data = wf.readframes(n_frames)
audio_array = np.frombuffer(audio_data, dtype=np.int16)

# 🔥 BALANCED PARAMETERS
frame_size = int(0.02 * frame_rate)  # 20 ms
threshold = 800              # ✔️ detects speech properly
min_speech_duration = 0.3    # ✔️ removes tiny noise
merge_gap = 0.6              # ✔️ merges nearby speech

speech_segments = []
start = None

# Detect speech
for i in range(0, len(audio_array), frame_size):
    frame = audio_array[i:i+frame_size]
    
    if len(frame) == 0:
        continue
    
    energy = np.mean(np.abs(frame))
    
    if energy > threshold:
        if start is None:
            start = i
    else:
        if start is not None:
            end = i
            speech_segments.append((start, end))
            start = None

# Filter small segments
filtered_segments = []
for start, end in speech_segments:
    duration = (end - start) / frame_rate
    if duration >= min_speech_duration:
        filtered_segments.append((start, end))

# Merge nearby segments
merged_segments = []
for seg in filtered_segments:
    if not merged_segments:
        merged_segments.append(seg)
    else:
        prev_start, prev_end = merged_segments[-1]
        curr_start, curr_end = seg
        
        gap = (curr_start - prev_end) / frame_rate
        
        if gap <= merge_gap:
            merged_segments[-1] = (prev_start, curr_end)
        else:
            merged_segments.append(seg)

# Create output folder
if not os.path.exists("output"):
    os.makedirs("output")

print("Speech Intervals:")

# Save segments
for idx, (start, end) in enumerate(merged_segments):
    start_time = start / frame_rate
    end_time = end / frame_rate
    
    print(f"{start_time:.2f}s - {end_time:.2f}s")
    
    segment = audio_array[start:end]
    
    out_file = f"output/speech_{idx+1}.wav"
    out_wf = wave.open(out_file, "wb")
    
    out_wf.setnchannels(1)
    out_wf.setsampwidth(2)
    out_wf.setframerate(frame_rate)
    out_wf.writeframes(segment.tobytes())
    out_wf.close()

print("Done! Clean speech segments saved.")