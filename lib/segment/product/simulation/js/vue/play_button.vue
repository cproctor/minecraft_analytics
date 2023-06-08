<script setup>

const props = defineProps(['playing'])

</script>

<template>
  <div id="play-button">
    <button @click="$emit('togglePlaying')">Playing is {{playing}}</button>
  </div>
</template>

<style>
#play-button {
  width: 150px;
}
</style>

