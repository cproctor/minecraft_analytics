# TODO: Perhaps only import what's needed?
# We could instead list the module and class here,
# And have the task import them 

from segment.product.transcript import SegmentTranscript
from segment.product.audio import SegmentAudio
from segment.product.video import SegmentVideo
from segment.product.logs import SegmentLogs
from segment.product.trace import SegmentTrace
from segment.product.joint_attention import SegmentJointAttention
from segment.product.cross_recurrence import SegmentCrossRecurrence
from segment.product.cross_recurrence_augmented import SegmentCrossRecurrenceAugmented
from segment.product.simulation import SegmentSimulation

PRODUCT_FORMATS = {
    'transcript': SegmentTranscript,
    'audio': SegmentAudio,
    'video': SegmentVideo,
    'logs': SegmentLogs,
    'trace': SegmentTrace,
    'joint_attention': SegmentJointAttention,
    'cross_recurrence': SegmentCrossRecurrence,
    'cross_recurrence_augmented': SegmentCrossRecurrenceAugmented,
    'simulation': SegmentSimulation,
}

