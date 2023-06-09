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
  <div id="play-button">
    <button @click="$emit('togglePlaying')">{{buttonText}}</button>
  </div>
</template>

<style>
#play-button {
  width: 150px;
}
</style>

