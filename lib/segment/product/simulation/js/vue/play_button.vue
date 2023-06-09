<script setup>
import { computed } from 'vue'

const props = defineProps(['playing', 'ended'])
const buttonText = computed(() => {
  if (props.playing) return "Pause"
  if (props.ended) return "Replay"
  return "Play"
})

</script>

<template>
  <div id="play-button" @click="$emit('togglePlaying')">
  <svg v-if="props.playing" class="play-button-icon" viewBox="0 0 24 24" 
  xmlns="http://www.w3.org/2000/svg">
    <path opacity="0" d="m0 0h24v24h-24z" />
    <g class="positive">
      <path d="m11.5 14.6 2.81-2.6-2.81-2.6z"/><path d="m12 2a10 10 0 1 0 10 10 10 10 0 0 0 -10-10zm4 11.18-3.64 3.37a1.74 1.74 0 0 1 -1.16.45 1.68 1.68 0 0 1 -.69-.15 1.6 1.6 0 0 1 -1-1.48v-6.74a1.6 1.6 0 0 1 1-1.48 1.7 1.7 0 0 1 1.85.3l3.64 3.37a1.6 1.6 0 0 1 0 2.36z"/>
    </g>
  </svg>
  <svg v-if="!props.playing" class="play-button-icon" viewBox="0 0 24 24" 
  xmlns="http://www.w3.org/2000/svg">
    <path opacity="0" d="m0 0h24v24h-24z" />
    <path class="positive" d="m12 2a10 10 0 1 0 10 10 10 10 0 0 0 -10-10zm-2 13a1 1 0 0 1 -2 0v-6a1 1 0 0 1 2 0zm6 0a1 1 0 0 1 -2 0v-6a1 1 0 0 1 2 0z" />
 </svg>
  </div>
</template>

<style>
#play-button {
  width: 110px;
}
.play-button-icon {
  width: 100px;
  padding: 16px;
}
.play-button-icon .positive {
  fill: #ecf0f1;
}
.play-button-icon:hover .positive {
  fill: #2ecc71;
}
</style>

