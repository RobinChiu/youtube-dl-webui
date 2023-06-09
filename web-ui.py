import gradio as gr
import config
import os
import subprocess

def getfilename(cmd):
    filename = None
    getfilename_cmd = '{} {}'.format(cmd, '--get-filename')
    process = subprocess.run(getfilename_cmd, shell=True, capture_output=True)
    if process.returncode == 0:
        filename = process.stdout.decode().strip()

    return filename

def download(options, url):
    log = ""
    print(options, url)
    cmd = '{} {} {}'.format(config.DL_CMD, options, url)

    filename = getfilename(cmd)
    if os.path.isfile(filename):
        print('remove file:', filename)
        os.remove(filename)

    # Run a shell command and capture its output and exit code in real time
    process = subprocess.Popen(cmd,
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=256)
    
    while True:
        output = process.stdout.readline()
        if output:
            log = log + output.decode()
            yield log, None
        else:
            break
    
    exit_code = process.wait()
    if exit_code != 1:
        # log.append('exit_code = {}'.format(exit_code))
        log = log + "exit_code = {}".format(exit_code)
    
    filename = os.path.join(config.DL_DIR, filename)
    if os.path.isfile(filename):
        yield log, filename
    else:
        yield log, None

def getfiles(dir = config.DL_DIR):
    result = []
    files = os.listdir(dir)
    for filename in files:
        filename = os.path.join(dir, filename)
        if os.path.isfile(filename):
            result.append(filename)
    print('result=', result)
    return result

def ffmpeg(options, ffmpeg_file):
    log = ""
    print(options, ffmpeg_file)
    cmd = '{} {} {}'.format(config.FFMPEG_CMD, options, ffmpeg_file)

    # Run a shell command and capture its output and exit code in real time
    process = subprocess.Popen(cmd,
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=256)
    
    while True:
        output = process.stdout.readline()
        if output:
            log = log + output.decode()
            yield log, None
        else:
            break
    
    exit_code = process.wait()
    if exit_code != 1:
        # log.append('exit_code = {}'.format(exit_code))
        log = log + "exit_code = {}".format(exit_code)
    
    ffmpeg_file = os.path.join(config.DL_DIR, ffmpeg_file)
    if os.path.isfile(ffmpeg_file):
        yield log, ffmpeg_file
    else:
        yield log, None


def main():
    # path = './videos'
    # examples = find_examples(path)
    # print(examples)

    examples = [
        ['--help', None, 'See a list of all options'],
        ['-F', 'https://www.youtube.com/watch?v=Cxzzg7L3Xgc', 'List all available formats of requested videos'],
        ['-f 249 -o output.mp4', 'https://www.youtube.com/watch?v=Cxzzg7L3Xgc', 'Download the format code 249 and output to output.mp4']
    ]

    ffmpeg_examples = [
        ['-i output.mp4 -vn -c:a libmp3lame -q:a 1', 'audio.mp3', 'extract the audio only'],
        ['-i output.mp4 -c:v copy -an', 'video.mp4', 'extract video only'],
        ['-i vocal.wav -i instrumental.wav -filter_complex amix=inputs=2:duration=longest', 'audio.mp3', 'combine two audio to one'],
        ['-i video.mp4 -i audio.mp3 -c copy -map 0:v:0 -map 1:a:0', 'output.mp4', 'combine audio and video to one']
    ]

    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.TabItem("Youtube download web-ui"):
                with gr.Row():
                    with gr.Column(scale=2):
                        note = gr.Markdown(label='Note', value='command note')
                        option = gr.Textbox(label="youtube-dl options")
                        url = gr.Textbox(label="Youtube url address")
                        btn_submit = gr.Button("Submit", variant="primary")

                        # video = gr.Video(label="Input video")
                        # job_type = gr.Dropdown(JOB_TYPE, label="Job_type")
                        # btn_submit = gr.Button("Submit")
                        # # btn_clear = gr.Button("Clear")
                        gr.Examples(examples, inputs=[option, url, note])
                    with gr.Column(scale=2):
                        log = gr.TextArea(placeholder="log")
                        video = gr.Video(label="download video")

                btn_submit.click(fn=download, inputs=[option, url], outputs=[
                                log, video])
                # btn_clear.click(lambda: None, None, video)
            
            with gr.TabItem("ffmpeg transform"):
                with gr.Row():
                    with gr.Column(scale=2):
                        ffmpeg_note = gr.Markdown(label='Note', value='command note')
                        ffmpeg_option = gr.Textbox(label="ffmpeg options")
                        ffmpeg_file = gr.Textbox(label="Output file")
                        ffmpeg_btn = gr.Button("Submit", variant="primary")

                        gr.Examples(ffmpeg_examples, inputs=[ffmpeg_option, ffmpeg_file, ffmpeg_note])
                    with gr.Column(scale=2):
                        ffmpeg_log = gr.TextArea(placeholder="log")
                        ffmpeg_video = gr.Video(label="download video")

                ffmpeg_btn.click(fn=ffmpeg, inputs=[ffmpeg_option, ffmpeg_file], outputs=[
                                ffmpeg_log, ffmpeg_video])
                # btn_clear.click(lambda: None, None, video)

            with gr.TabItem("downloads file list"):
                with gr.Row():
                    with gr.Column(scale=2):
                        filelist = getfiles()
                        files = gr.Files(value=filelist)
                        refrest_btn = gr.Button("Refresh", variant="primary")
                refrest_btn.click(fn=getfiles, inputs=[], outputs=[files])
            

    demo.queue(concurrency_count=5)
    demo.launch(debug=True, server_name='0.0.0.0')

main()

if __name__ == '__main__':
    main()
