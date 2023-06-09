<script setup>
import PlayButton from './play_button.vue'
import Timeline from './timeline.vue'
import { ref, computed, onMounted } from 'vue'

const playing = ref(true)
const beginDate = ref(new Date(window.DATA.params.timespan[0]))
const duration = ref(
  Date.parse(window.DATA.params.timespan[1]) - 
  Date.parse(window.DATA.params.timespan[0])
)
const t = ref(0) 
const speed = ref(5)
const lastFrameTime = ref(undefined)
const ended = computed(() => t.value == duration.value)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

function play() {
  playing.value = true
  animateSim()
}
function pause() {
  playing.value = false
}
function seek(tSeek) {
  t.value = tSeek
  updateSim()
}

function togglePlaying() {
  if (playing.value) {
    pause()
  } else {
    if (t.value == duration.value) t.value = 0
    play()
  }
}

function animateSim() {
  if (lastFrameTime.value === undefined) {
    lastFrameTime.value = new Date()
  }
  else {
    const now = new Date()
    const elapsed = speed.value * (now.getTime() - lastFrameTime.value.getTime())
    if (t.value + elapsed > duration.value) {
      t.value = duration.value
      playing.value = false
    }
    else if (t.value + elapsed < 0) {
      t.value = 0
      playing.value = false
    }
    else {
      t.value += elapsed
    }
    updateSim()
  }
  if (playing.value) {
    requestAnimationFrame(animateSim)
  } else {
    lastFrameTime.value = undefined
  }
}

function updateSim() {
  const seekDate = new Date(beginDate.value.getTime() + t.value)
  window.sim.seek(seekDate)
}

function handleKeydown(evt) {
  if (evt.key === ' ') {
    togglePlaying()
  }
}

if (playing.value) animateSim()

</script>

<template>
  <div id="inner-controls">
    <PlayButton :playing="playing" :ended="ended" @toggle-playing="togglePlaying" />
    <Timeline :playing="playing" :duration="duration" :t="t" 
      @play="play"
      @pause="pause"
      @seek="seek"
    />
  </div>
</template>

<style>
#inner-controls {
  display: flex;
}
</style>
