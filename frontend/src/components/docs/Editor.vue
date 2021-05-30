<template>
  <div class="home" v-title data-title="请开始编辑你的文档吧！">
    <mavon-editor
      v-model="content"
      ref="md"
      :subfield="false"
      @change="change"
      style="min-height: 600px; z-index:1"
      :editable="modify_right"
      @save="save_docs()"
    />
  </div>
</template>

<script type="text/javascript" charset="utf-8" src="js/html2canvas.js"></script>
<script type="text/javascript" charset="utf-8" src="js/jsPdf.debug.js"></script>
<script
  type="text/javascript"
  charset="utf-8"
  src="js/canvas2image.js"
></script>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script src="https://cdn.bootcss.com/jspdf/1.3.4/jspdf.debug.js"></script>
<script>
import { mavonEditor } from "mavon-editor";
import memberAvatar from "../team/memberAvatar";
import "mavon-editor/dist/css/index.css";
import axios from "axios";
import moment from "moment";
import "@/utils/htmlToPdf.js";
import docxtemplater from "docxtemplater";
import PizZip from "pizzip";
import JSZipUtils from "jszip-utils";
import { saveAs } from "file-saver";
import privilegePane from "./privilegePane.vue";
import $ from "jquery";
import html2canvas from "html2canvas";
import _ from "lodash";
import Measurement from "../../utils/caretposition";

//sharedb
import ReconnectingWebSocket from "reconnecting-websocket";
var sharedb = require("sharedb/lib/client");
var StringBinding = require("../../utils/sharedb-string-binding");

// Open WebSocket connection to ShareDB server
var socket;
var connection;

//end sharedb

export default {
  name: "Home",
  components: {
    mavonEditor,
    memberAvatar,
    privilegePane,
  },
  props: ["userList"],
  data() {
    return {
      htmlTitle: "导出文件",
      //定时刷新正在编辑的用户列表
      timer: "",
      inviteuser: "",
      invitedata: [],
      form: {
        content: "",
        username: "",
        title: "",
      },
      content: "",
      html: "",
      configs: {},
      collapsed: false,
      moment,
      keyword: "",
      comment: [],
      modify_history: [],
      watch_right: false,
      modify_right: true,
      discuss_right: true,
      share_right: true,
      userId: 0,
    };
  },
  methods: {
    exportReport() {
      exportReportTemplet();
    },
    //刷新正在编辑的用户列表的方法
    exportWord: function() {
      let _this = this;
      // 读取并获得模板文件的二进制内容
      JSZipUtils.getBinaryContent("/template.docx", function(error, content) {
        // input.docx是模板。我们在导出的时候，会根据此模板来导出对应的数据
        // 抛出异常
        if (error) {
          console.log(error);
          throw error;
        }

        // 创建一个JSZip实例，内容为模板的内容
        let zip = new PizZip(content);
        // 创建并加载docxtemplater实例对象
        let doc = new docxtemplater().loadZip(zip);
        // 设置模板变量的值
        doc.setData({
          ..._this.form,
          table: _this.tableData,
        });

        try {
          // 用模板变量的值替换所有模板变量
          doc.render();
        } catch (error) {
          // 抛出异常
          let e = {
            message: error.message,
            name: error.name,
            stack: error.stack,
            properties: error.properties,
          };
          console.log(JSON.stringify({ error: e }));
          throw error;
        }

        // 生成一个代表docxtemplater对象的zip文件（不是一个真实的文件，而是在内存中的表示）
        let out = doc.getZip().generate({
          type: "blob",
          mimeType:
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        });
        // 将目标文件对象保存为目标类型的文件，并命名
        saveAs(out, "Docs.docx");
      });
    },
    // 所有操作都会被解析重新渲染
    change(value, render) {
      // render 为 markdown 解析后的结果[html]
      this.html = render;
    },
    successmsg(message) {
      this.$message.success(message);
    },
    errormsg(message) {
      this.$message.error(message);
    },
    warningmsg(message) {
      this.$message.warning(message);
    },
    callback() {},
    // 提交
    save_docs() {
      var _this = this;
      let formData = new FormData();
      formData.append("content", this.content);
      formData.append("DocumentID", this.$route.params.id);
      formData.append("username", localStorage.getItem("token"));
      let config = {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      };
      axios
        .post("http://localhost:5000/api/modify_doc/", formData, config)
        .then(function(response) {
          if (response.data.message == "success") {
            _this.successmsg("保存成功");
          } else {
            console.log("失败");
          }
        })
        .catch(function(error) {
          console.log("Fail", error);
        });
    },
    load_data(id) {
      let formData = new FormData();
      formData.append("DocumentID", id);
      formData.append("username", localStorage.getItem("token"));
      let config = {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      };
      var _this = this;
      axios
        .post("http://localhost:5000/api/get_doccontent/", formData, config)
        .then(function(response) {
          if (response.data.message == "success") {
            _this.content = response.data.content;
            _this.form.content = response.data.content;
            _this.form.username = localStorage.getItem("token");
          } else {
            console.log("失败");
          }
        })
        .catch(function(error) {
          console.log("Fail", error);
        });
    },
    getCaretXY() {
      var textBox = document.querySelector(".auto-textarea-input");
      var caretPosition = Measurement.caretPos(textBox, "self");
      return caretPosition;
    },
    renderVCaret(x, y, bgColor) {
      const styleObj = {
        height: "20px",
        width: "3px",
        "background-color": "rgba(153, 50, 233, 0.5)",
        position: "absolute",
        left: `${x}px`,
        top: `${y}px`,
        "z-index": 2,
      };
      let vCaretDom = document.querySelector("#vcaret");
      if (vCaretDom) {
        for (let i in styleObj) {
          vCaretDom.style[i] = styleObj[i];
        }
      } else {
        let vcaret = document.createElement("div");
        vcaret.id = "vcaret";
        for (let i in styleObj) {
          vcaret.style[i] = styleObj[i];
        }
        document.querySelector(".auto-textarea-wrapper").appendChild(vcaret);
      }
    },
    throttleRenderVCaret2: _.throttle(
      function(x, y, bgColor) {
        this.renderVCaret(x, y, bgColor);
      },
      500,
      {
        leading: true,
        trailing: false,
      }
    ),
    initCoDoc(docId) {
      var _this = this;
      const userId = localStorage.getItem("userid");
      const documentId = _this.$route.params.id;

      socket = new ReconnectingWebSocket(
        `ws://localhost:8088?documentId=${documentId}&userId=${userId}`
      );
      connection = new sharedb.Connection(socket);
      connection.on("error", (err) => {
        console.log(err);
      });
      var element = document.querySelector(".auto-textarea-input");
      var doc = connection.get("multiDoc", docId);

      element.addEventListener("input", () => {
        const positionObj = _this.getCaretXY();
        socket.send(
          JSON.stringify({
            action: "vCaretInsert",
            a: "vCaretInsert",
            data: {
              left: positionObj.left,
              top: positionObj.top,
              source: localStorage.getItem("token"),
            },
          })
        );
      });

      //这个监听是为了改变content从而更新md预览区视图
      doc.on("op", () => {
        _this.$nextTick(() => {
          _this.content = element.value;
        });
      });

      //监听事件
      socket.addEventListener("message", (event) => {
        try {
          var message = getWsEventData(event);
          const action = message.action;
          if (["members", "vCaretInsert"].includes(action)) {
            handleAction[message.action](message);
          }
        } catch (err) {
          console.warn("Failed to parse message", err);
          return;
        }
      });

      const handleAction = {
        members: (message) => {
          _this.$emit("userListChange", _.uniqBy(message.data, "name"));
        },
        vCaretInsert: (message) => {
          if (message.data.source !== localStorage.getItem("token")) {
            _this.throttleRenderVCaret2(message.data.left, message.data.top);
          }
        },
      };

      //订阅该文档的更改
      doc.subscribe(function(err) {
        if (err) throw err;
        setTimeout(() => {
          //这个延时是为了等element生成出来
          var binding = new StringBinding(element, doc, ["content"]);
          binding.setup();
        }, 1000);
      });
    },
  },
  destroyed() {
    clearInterval(this.timer);
  },
  mounted: function() {
    this.load_data(this.$route.params.id);
    this.initCoDoc(this.$route.params.id);
  },
};

const getWsEventData = (event) => {
  let data = {};
  try {
    data = typeof event.data === "string" ? JSON.parse(event.data) : event.data;
  } catch (error) {
    console.log(error);
    console.error("getWsEventData error");
  }
  return data;
};
</script>
<style></style>
