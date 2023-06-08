<script setup>
import PlayButton from './play_button.vue'
import Timeline from './timeline.vue'
import { ref } from 'vue'

const playing = ref(true)
const beginDate = ref(new Date(window.DATA.params.timespan[0]))
const duration = ref(
  Date.parse(window.DATA.params.timespan[1]) - 
  Date.parse(window.DATA.params.timespan[0])
)
const playHead = ref(0)
const speed = ref(1)
const latestAnimationFrameTime = ref(new Date())

function togglePlaying() {
  playing.value = !playing.value
  if (playing.value) animateSim()
}

function animateSim() {
  latestAnimationFrameTime.value = new Date()
  requestAnimationFrame(animationLoop)
}

// Doesn't currently invoke the sim. IS something wrong with the if-statement conditions?
function animationLoop() {
  const currentTime = new Date()
  const elapsed = speed.value * (currentTime.getTime() - latestAnimationFrameTime.value.getTime())
  if (playHead.value + elapsed > duration.value) {
    window.sim.seek(new Date(beginDate.value.getTime() + playHead.value))
    playHead.value = duration.value
    playing.value = false
  }
  else if (playHead.value + elapsed < 0) {
    window.sim.seek(beginDate.value)
    playHead.value = 0
    playing.value = false
  }
  else {
    playHead.value += elapsed
  }
  if (playing.value) requestAnimationFrame(animationLoop)
}

if (playing.value) animateSim()

</script>

<template>
  <PlayButton :playing="playing" @toggle-playing="togglePlaying" />
  <Timeline />
</template>

<style>
</style>
