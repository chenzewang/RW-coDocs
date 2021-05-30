<template>
  <a-modal
    title="创建文档"
    :visible="modalVisiable"
    @ok="createdoc"
    @cancel="cancelcreate"
  >
    <template>
      <a-form-model
        :model="newdocform"
        :label-col="labelCol"
        :wrapper-col="wrapperCol"
      >
        <a-form-model-item label="文档标题">
          <a-input v-model="newdocform.title" />
        </a-form-model-item>
        <a-form-model-item label="协作者权限">
          <div>
            <div :style="{ borderBottom: '1px solid #E9E9E9' }">
              <a-checkbox
                :indeterminate="indeterminate"
                :checked="checkAll"
                @change="onCheckAllChange"
                >Check all</a-checkbox
              >
            </div>
            <a-checkbox-group
              v-model="checkedList"
              :options="plainOptions"
              @change="onChange"
            />
          </div>
        </a-form-model-item>
        <a-form-model-item label="模版选择">
          <div>
            <a-radio-group v-model="templateValue">
              <a-radio :value="1">空白文档 </a-radio>
              <a-radio :value="2">模版 1 </a-radio>
              <a-radio :value="3">模版 2 </a-radio>
            </a-radio-group>
          </div>
        </a-form-model-item>
      </a-form-model>
    </template>
  </a-modal>
</template>
<script type="text/ecmascript-6">
import axios from "axios";

const plainOptions = ['修改', '评论', '分享'];
const defaultCheckedList = ['修改', '评论'];
export default {
  props:["modalVisiable"],
  data() {
    return {
      templateValue:1,
      checkedList: defaultCheckedList,
      indeterminate: true,
      indeterminateTem: true,
      checkAll: false,
      plainOptions,
      top: 0,
      visible: false,
      DocumentID: {
        type: Number,
      },
      newdocform:{
        title:"",
        modify_right:0,
        share_right:0,
        discuss_right:0,
        content:""
      },
      labelCol: { span: 4 },
      wrapperCol: { span: 14 },
      content2:"# 欢迎使用 文档模版1\n"+
        " ------\n"+
        "为了更好的使用文档,**graphene Markdown** 提供了两套模版系统 \n"+
        "> * 整理知识，学习笔记\n"+
        "> * 发布日记，杂文，所见所想\n"+
        "> * 撰写发布技术文稿（代码支持）\n"+
        "> * 撰写发布学术论文\n"+
        "![cmd-markdown-logo](https://img0.baidu.com/it/u=3535222276,3943130922&fm=26&fmt=auto&gp=0.jpg)\n",
      content3:
        "# 欢迎使用 文档模版2\n"+
        " ------\n"+
        "为了更好的使用文档,**graphene Markdown** 提供了两套模版系统 \n"+
        "以下是markdown简要使用说明\n"+
        "# Title1\n"+
        "## Title2\n"+
        "### Title3\n"+
        "content\n"+
        "==\n"+
        "content2\n"+
        "--\n"+
        "content3\n"+
        "--\n"+
        "* name\n"+
        "- name\n"+
        "+ name\n"+
        "* [I'm an inline-style link](https://www.google.com)\n"+
        "* Inline `code` has `back-ticks around` it.\n"+
        "```javascript\n"+
        "var s = \"JavaScript syntax highlighting\";\n"+
        "alert(s);\n"+
        "```"
    };
  },
  methods: {
    successmsg(message) {
      this.$message.success(message);
    },
    errormsg(message) {
      this.$message.error(message);
    },
    onChange(checkedList) {
      this.indeterminate = !! checkedList.length && checkedList.length < plainOptions.length;
      this.checkAll = checkedList.length === plainOptions.length;
    },

    onCheckAllChange(e) {
      Object.assign(this, {
        checkedList: e.target.checked ? plainOptions : [],
        indeterminate: false,
        checkAll: e.target.checked,
      });
    },

    createdoc(){
      this.checkedList.forEach(element => {
        if(element=="修改")this.newdocform.modify_right=1;
        if(element=="评论")this.newdocform.discuss_right=1;
        if(element=="分享")this.newdocform.share_right=1;
      });
      if (this.newdocform.title == ""){
              this.errormsg("标题为空");
              return;
            }
      switch(this.templateValue){
        case 1:
          break;
        case 2:
          this.newdocform.content=this.content2;
          break;
        case 3:
          this.newdocform.content=this.content3;
          break;
      }
      this.newdoc();
    },
    cancelcreate(){
      this.$emit("update:modalVisiable",false)
    },
    shownewdocform(){
      this.$emit("update:modalVisiable",true)
    },
    newdoc() {
      var _this=this;
      let formData = new FormData();
      formData.append("username", localStorage.getItem("token"));
      formData.append("title", this.newdocform.title);
      formData.append("modify_right", this.newdocform.modify_right);
      formData.append("share_right", this.newdocform.share_right);
      formData.append("discuss_right", this.newdocform.discuss_right);
      formData.append("content", this.newdocform.content);
      let config = {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      };
      axios.post("http://localhost:5000/api/create_personal_doc/", formData, config)
        .then(function (response) {
          console.log('---------创建成功',response);
          if (response.data.message == "success") {
            _this.successmsg("创建成功");
            setTimeout(() => {
              _this.$router.push({ name: 'Docs2', params: { id: response.data.newDocumentId }})
            }, 1500);
          }
          else {
            _this.errormsg("创建失败，请尝试刷新后再次创建1");
          }
        })
        .catch(function (error) {
          console.log(error)
          _this.errormsg("创建失败，请尝试刷新后再次创建2");
        });
    },
  },
  mounted() {

  },
};
</script>
<style></style>
