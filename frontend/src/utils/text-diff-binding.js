module.exports = TextDiffBinding;

function TextDiffBinding(element) {
  this.element = element;
}

/**
 * TextDiffBinding是基类，必须继承时定义`_get()`, `_insert(index, length)`, and `_remove(index, length)这三个方法
 */
TextDiffBinding.prototype._get = TextDiffBinding.prototype._insert = TextDiffBinding.prototype._remove = function () {
  throw new Error('`_get()`, `_insert(index, length)`, and `_remove(index, length)` prototype methods must be defined.');
};

/**
 * 获取dom的value属性的值
 * @returns 
 */
TextDiffBinding.prototype._getElementValue = function () {
  var value = this.element.value;
  // IE and Opera replace \n with \r\n. Always store strings as \n
  return value.replace(/\r\n/g, '\n');
};

/**
 * 获取文本结束位置的下标
 * @param {*} previous 
 * @param {*} value 
 * @returns 
 */
TextDiffBinding.prototype._getInputEnd = function (previous, value) {
  if (this.element !== document.activeElement) return null;
  var end = value.length - this.element.selectionStart;
  if (end === 0) return end;
  if (previous.slice(previous.length - end) !== value.slice(value.length - end)) return null;
  return end;
};

/**
 * 监听input事件，获取找到文本变更地方，执行相应的_remove或者_insert
 * @returns 
 */
TextDiffBinding.prototype.onInput = function () {
  var previous = this._get();
  var value = this._getElementValue();
  if (previous === value) return;

  var start = 0;
  // Attempt to use the DOM cursor position to find the end 尝试使用DOM游标位置来查找结束坐标
  var end = this._getInputEnd(previous, value);
  if (end === null) {
    // If we failed to find the end based on the cursor, do a diff. When
    // ambiguous, prefer to locate ops at the end of the string, since users
    // more frequently add or remove from the end of a text input
    //如果我们不能根据光标找到末尾，做一个diff（找到previous与value的差异所在）。
    //当有歧义时，倾向于在字符串的末尾定位操作符，因为用户更频繁地从文本输入的末尾添加或删除操作符

    //从0位置开始找，找到previous与value第一个不一样字符的位置
    while (previous.charAt(start) === value.charAt(start)) {
      start++;
    }
    end = 0;

    //从尾部开始找，找到previous与value第一个不一样字符的位置
    while (
      previous.charAt(previous.length - 1 - end) === value.charAt(value.length - 1 - end) &&
      end + start < previous.length &&
      end + start < value.length
    ) {
      end++;
    }

  } else {
    while (
      previous.charAt(start) === value.charAt(start) &&
      start + end < previous.length &&
      start + end < value.length
    ) {
      start++;
    }
  }

  if (previous.length !== start + end) {
    var removed = previous.slice(start, previous.length - end); //被删除的文本
    this._remove(start, removed);
  }
  if (value.length !== start + end) {
    var inserted = value.slice(start, value.length - end); //被插入的文本
    this._insert(start, inserted);
  }
};

//执行远端传来的insert操作
TextDiffBinding.prototype.onInsert = function (index, length) {
  this._transformSelectionAndUpdate(index, length, insertCursorTransform);
};


/**
 * insert后，游标的位置
 * @param {*} index 
 * @param {*} length 
 * @param {*} cursor 
 * @returns 
 */
function insertCursorTransform(index, length, cursor) {
  return (index < cursor) ? cursor + length : cursor;
}

TextDiffBinding.prototype.onRemove = function (index, length) {
  this._transformSelectionAndUpdate(index, length, removeCursorTransform);
};

/**
 * delete后，游标的位置
 * @param {*} index 
 * @param {*} length 
 * @param {*} cursor 
 * @returns 
 */
function removeCursorTransform(index, length, cursor) {
  return (index < cursor) ? cursor - Math.min(length, cursor - index) : cursor;
}

/**
 * 更新编辑域的值和更新Selection
 * @param {*} index 
 * @param {*} length 
 * @param {*} transformCursor 
 */
TextDiffBinding.prototype._transformSelectionAndUpdate = function (index, length, transformCursor) {
  if (document.activeElement === this.element) {
    var selectionStart = transformCursor(index, length, this.element.selectionStart);
    var selectionEnd = transformCursor(index, length, this.element.selectionEnd);
    var selectionDirection = this.element.selectionDirection; //selection的方向
    this.update();
    this.element.setSelectionRange(selectionStart, selectionEnd, selectionDirection);
  } else {
    this.update();
  }
};

/**
 * 更新element的value属性值
 * @returns 
 */
TextDiffBinding.prototype.update = function () {
  var value = this._get();
  if (this._getElementValue() === value) return;
  this.element.value = value;
};