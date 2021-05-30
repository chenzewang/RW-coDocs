var TextDiffBinding = require('./text-diff-binding');

module.exports = StringBinding;

function StringBinding(element, doc, path) {
  TextDiffBinding.call(this, element);
  this.doc = doc;
  this.path = path || [];
  this._opListener = null;
  this._inputListener = null;
}

//继承TextDiffBinding
StringBinding.prototype = Object.create(TextDiffBinding.prototype);
StringBinding.prototype.constructor = StringBinding;

//开始监听
StringBinding.prototype.setup = function () {
  this.update();
  this.attachDoc();
  this.attachElement();
};

//销毁监听
StringBinding.prototype.destroy = function () {
  this.detachElement();
  this.detachDoc();
};

//开始监听输入区域（input或textarea）的输入
StringBinding.prototype.attachElement = function () {
  var binding = this;
  this._inputListener = function () {
    binding.onInput();
  };
  this.element.addEventListener('input', this._inputListener, false);
};

//销毁监听输入区域（input或textarea）的输入
StringBinding.prototype.detachElement = function () {
  this.element.removeEventListener('input', this._inputListener, false);
};

//开始监听doc的变化，这个doc指所协同编辑的文本，由sharedb生成
StringBinding.prototype.attachDoc = function () {
  var binding = this;
  this._opListener = function (op, source) {
    binding._onOp(op, source);
  };
  this.doc.on('op', this._opListener);
};

//销毁监听doc的变化，这个doc指所协同编辑的文本，由sharedb生成
StringBinding.prototype.detachDoc = function () {
  this.doc.removeListener('op', this._opListener);
};

//op事件的监听函数
StringBinding.prototype._onOp = function (op, source) {
  if (source === this) return;
  if (op.length === 0) return;
  if (op.length > 1) {
    throw new Error('Op with multiple components emitted');
  }
  var component = op[0]; //op的例子：[{p: ["content", 27], si: "1"}]
  if (isSubpath(this.path, component.p)) {
    this._parseInsertOp(component);
    this._parseRemoveOp(component);
  } else if (isSubpath(component.p, this.path)) {
    this._parseParentOp();
  }
};

StringBinding.prototype._parseInsertOp = function (component) {
  if (!component.si) return;
  var index = component.p[component.p.length - 1]; //即p这个数组的最后一个元素
  var length = component.si.length; //所插入的字符串的长度
  this.onInsert(index, length);
};

StringBinding.prototype._parseRemoveOp = function (component) {
  if (!component.sd) return;
  var index = component.p[component.p.length - 1];
  var length = component.sd.length;
  this.onRemove(index, length);
};

StringBinding.prototype._parseParentOp = function () {
  this.update();
};

StringBinding.prototype._get = function () {
  var value = this.doc.data;
  for (var i = 0; i < this.path.length; i++) {
    var segment = this.path[i];
    value = value[segment];
  }
  return value;
};

StringBinding.prototype._insert = function (index, text) {
  var path = this.path.concat(index);
  var op = {
    p: path,
    si: text
  };
  this.doc.submitOp(op, {
    source: this
  });
};

StringBinding.prototype._remove = function (index, text) {
  var path = this.path.concat(index);
  var op = {
    p: path,
    sd: text
  };
  this.doc.submitOp(op, {
    source: this
  });
};


/**
 * 是否是所订阅的path
 * @param {*} path 
 * @param {*} testPath 
 * @returns 
 */
function isSubpath(path, testPath) {
  for (var i = 0; i < path.length; i++) {
    if (testPath[i] !== path[i]) return false;
  }
  return true;
}