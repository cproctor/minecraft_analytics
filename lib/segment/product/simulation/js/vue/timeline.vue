<script setup>
import { ref, computed, reactive, onMounted } from 'vue'

const props = defineProps(['playing', 'duration', 't'])
const emit = defineEmits(['pause', 'seek', 'play'])
const height = ref(80)
const width = ref(100)
const playHeadPosition = computed(() => width.value * (props.t / props.duration))
const playingBeforeMouseDown = ref(props.playing)
const scrubbing = ref(false)

onMounted(() => {
  measureWidth()
  window.addEventListener('resize', measureWidth) 
})

function measureWidth() {
  const rect = document.getElementById("timeline-rect")
  width.value = rect.getBoundingClientRect().width
}

function handleMousedown(evt) {
  playingBeforeMouseDown.value = props.playing
  if (props.playing) emit('pause')
  scrubbing.value = true
  seekAtMouseX(evt)
}
function handleMouseup(evt) {
  if (scrubbing.value) {
    scrubbing.value = false
    if (playingBeforeMouseDown.value) {
      emit('play')
    }
  }
}
function handleMousemove(evt) {
  if (scrubbing.value) seekAtMouseX(evt)
}
function seekAtMouseX(evt) {
  const relativeMouseX = evt.clientX - evt.target.getBoundingClientRect().left
  const tScrub = props.duration * (relativeMouseX / width.value)
  emit('seek', tScrub)
}
function handleMouseenter(evt) {
}
function handleMouseleave(evt) {
  /*
  if (scrubbing.value) {
    scrubbing.value = false
    if (playingBeforeMouseDown.value) {
      emit('play')
    }
  }
  */
}

const playHeadStyle = reactive({
  transform: 'translate(' + playHeadPosition + ', 0)'
})

</script>

<template>
  <div id="timeline">
    <svg width="100%" :height="height">
      <rect id="timeline-rect" x="0" y="0" height="100%" width="100%" 
       @mousedown="handleMousedown" 
       @mouseup="handleMouseup" 
       @mousemove="handleMousemove"
       @mouseenter="handleMouseenter" 
       @mouseleave="handleMouseleave" 
      />
      <g id="play-head" :style="playHeadStyle">
        <line :x1="playHeadPosition" y1="0" :x2="playHeadPosition" :y2="height" />
        <circle :cx="playHeadPosition" cy="0" r="6" />
      </g>
    </svg>
  </div>
</template>

<style>
#timeline {
  flex: 1 1;
  padding: 25px;
}
#timeline svg {
}
#timeline svg rect {
  stroke-width: 1px;
  stroke: black;
  fill: #ecf0f1;
  cursor: grab;
}
#play-head {
  stroke: #e74c3c;
  fill: #e74c3c;
  cursor: grab;
}
#play-head line {
  stroke-width: 2px;
}
</style>
