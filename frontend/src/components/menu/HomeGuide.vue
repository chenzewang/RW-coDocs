<template>
  <div>
    <div>
      <a-button @click="createDoc">新建文档</a-button>
      <createDosModal :modalVisiable.sync="modalVisiable"></createDosModal>
    </div>

    <p class="title">最近浏览</p>
    <recentDocs></recentDocs>
    <p class="title">收藏</p>
    <snshrineDocs></snshrineDocs>
  </div>
</template>
<script type="text/ecmascript-6">
import recentDocs from "./RecentDocs"
import snshrineDocs from "./EnshrineDocs"
import createDosModal from "../docs//createDosModal"


export default {
    components:{recentDocs,snshrineDocs,createDosModal},

    data(){
        return {modalVisiable:false}
    },
    methods:{
      createDoc(){
        this.modalVisiable=true
      }
    },
}
</script>
<style scoped>
.title {
  text-align: center;
  font-size: 20px;
}
</style>
