from enum import Enum


class GenerationStatus(Enum):
    unknown = ''
    received = 'RECEIVED'
    transcribe_task_started = 'TRANSCRIBE_TASK_STARTED'
    transcribe_stage_1 = 'TRANSCRIBE_STAGE_1'
    transcribe_stage_2 = 'TRANSCRIBE_STAGE_2'
    transcribe_stage_3 = 'TRANSCRIBE_STAGE_3'
    transcribe_done = 'TRANSCRIBE_DONE'
    prompt = 'PROMPT'
    task_sent = 'TASK_SENT'
    generate_task_started = 'GENERATE_TASK_STARTED'
    loading_source = 'LOADING_SOURCE'
    beginning_generation = 'BEGINNING_GENERATION'
    generating = 'GENERATING'
    decompressing = 'DECOMPRESSING'
    saving = 'SAVING'
    success = 'SUCCESS'
    failure = 'FAILURE'


class ExtendDirection(Enum):
    left = 'left'
    right = 'right'

