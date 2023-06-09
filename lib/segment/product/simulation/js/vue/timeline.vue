<script setup>
import { ref, computed } from 'vue'

const props = defineProps(['playing', 'duration', 't'])
const emit = defineEmits(['pause', 'seek', 'play'])
const height = ref(100)
const width = ref(400)
const playHeadPosition = computed(() => width.value * (props.t / props.duration))
const playingBeforeMouseDown = ref(props.playing)
const scrubbing = ref(false)

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
  console.log("LEAVE")
  if (scrubbing.value) {
    scrubbing.value = false
    if (playingBeforeMouseDown.value) {
      emit('play')
    }
  }
}

</script>

<template>
  <div id="timeline">
    <svg width="600px" :height="height">
      <rect x="0" y="0" height="100" width="400" 
       @mousedown="handleMousedown" 
       @mouseup="handleMouseup" 
       @mousemove="handleMousemove"
       @mouseenter="handleMouseenter" 
       @mouseleave="handleMouseleave" 
      />
      <line id="play-head" :x1="playHeadPosition" y1="0" :x2="playHeadPosition" :y2="height" />
    </svg>
  </div>
</template>

<style>
#timeline {
  flex: 1 1;
}
svg {
  transform: translate(25px, 25px);
}
svg rect {
  stroke-width: 1px;
  stroke: black;
  fill: white;
}
#play-head {
  stroke-width: 2px;
  stroke: red;
}
</style>
