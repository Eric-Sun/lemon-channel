jQuery.fn.validatelus = function(config) {
	config = jQuery.extend({
		errtype: "realtime",
		errel: "span",
		errelpos: "normal", //"after"时代表错误提示元素紧跟input元素之后
		prefixclass: " input-notification png_bg ",
		tipcss: "attention",
		errcss: "error",
		rightcss: "success",	//"none"时代表无正确提示
		submittype: "auto",
		msgs: {
		required: "请填写{0}",
		email: "请输入正确的邮箱地址.",
		equalTo: "两次输入不一致, 请重新输入.",
		accept: "格式不正确.",
		range: "必须在{0}-{1}个字符之间.",
		num: "只充许输入数字, 请重新输入",
		url: "请输入正确的网址格式, 如http://test.com",
		minurl: "请输入正确的网址格式, 如test.com. 不加http://前缀",
		mobile: "请输入正确的手机号码.",
		phone: "请输入正确的电话号码.",
		mobilephone: "请输入正确的联系电话.",
		max: "Please enter a value less than or equal to {0}.",
		min: "Please enter a value greater than or equal to {0}."
		},
		callback:function(){return true;}
	},config||{});
	
	$.format = function(source, params) {
		if(arguments.length == 1) 
			return source;
		if ( arguments.length > 2 && params.constructor != Array  ) {
			params = $.makeArray(arguments).slice(1);
		}
		if ( params.constructor != Array ) {
			params = [ params ];
		}
		$.each(params, function(i, n) {
			source = source.replace(new RegExp("\\{" + i + "\\}", "g"), n);
		});
		return source;
	};
	
	$.showmsg = function(elementid, content) {
		var tipelement = $("#"+elementid+" ~ "+config.errel).filter("."+config.tipcss);	//原说明文字
		var errelement = $("#"+elementid+" ~ "+config.errel).filter("."+config.errcss);	//新增错误信息
		if(errelement.length>0) {
			errelement.remove();
		}
		if(tipelement.length>0) {
			tipelement.hide();	//隐藏原说明文字
		}
		tipelement = $("#"+elementid+" ~ "+config.errel).filter("."+config.rightcss);	//正确提示信息
		if(tipelement.length>0) {
			tipelement.remove();	//移除原正确提示信息
		}
		//自动新增错误信息
		var htmlcon = "<"+config.errel+" name='luc_error_msg' id='luc_err_"+elementid+"' class='"+config.prefixclass+config.errcss+"'";
		if(config.errtype == "alert")
			htmlcon += " style='display:none;'";
		htmlcon += ">"+content+"</"+config.errel+">";
		if(config.errelpos == "after") {
			$("#"+elementid).after(htmlcon);	//紧随input元素
		} else {
			var ff = $("#"+elementid+" ~ "+config.errel);
			var sz =ff.size();
			if(sz > 0) {
				$(ff.get(sz-1)).parent().append(htmlcon);	//自动新增错误信息
			} else {
				$("#"+elementid).parent().append(htmlcon);	//自动新增错误信息
			}
		}
	}
	
	$.resetmsg = function(elementid) {
		var tipelement = $("#"+elementid+" ~ "+config.errel).filter("."+config.tipcss);	//原说明文字
		if(tipelement.length>0) {
			tipelement.remove();	//移除原说明文字
		}
		var errelement = $("#"+elementid+" ~ "+config.errel).filter("."+config.errcss);	
		errelement.remove();//移除错误信息
		//config.rightcss == none则无正确提示信息
		if(config.rightcss != "none") {
			var tipelement = $("#"+elementid+" ~ "+config.errel).filter("."+config.rightcss);	//正确提示信息
			if(tipelement.length>0) {
				tipelement.remove();	//移除原正确提示信息
			}
			var ff = $("#"+elementid+" ~ "+config.errel);
			var sz =ff.size();
			if(sz > 0) {
				var htmlcon = "<"+config.errel+" id='luc_right_"+elementid+"' class='"+config.prefixclass+config.rightcss+"'";
				if(config.errtype == "alert")
					htmlcon += " style='display:none;'";
				htmlcon += ">&nbsp;</"+config.errel+">";
				$(ff.get(sz-1)).parent().append(htmlcon);	//自动新增正确提示信息
			} else {
				var htmlcon = "<"+config.errel+" id='luc_right_"+elementid+"' class='"+config.prefixclass+config.rightcss+"'";
				if(config.errtype == "alert")
					htmlcon += " style='display:none;'";
				htmlcon += ">&nbsp;</"+config.errel+">";
				$("#"+elementid).parent().append(htmlcon);	//自动新增正确提示信息
			}
		}
	}
	
	$.hasErrmsg = function(elementid) {
		return $("#"+elementid+" ~ "+config.errel).filter("."+config.errcss).size() > 0;
	}
	
	$.validateElement = function(elementid) {
		var element = $("#"+elementid);
		var errelement = $("#"+elementid+" ~ "+config.errel).filter("."+config.errcss);	//自动新增错误信息
		var val = element.val();
		if(arguments.length > 1 && $.hasErrmsg(elementid)) {
			return false;
		}
		if(element.attr("irequired")) {
			var required = element.attr("irequired");
			//required = required.split("|-|");
			if(!val) {
				$.showmsg(elementid, $.format(msgs.required, required));
				return false;
			} else {
				$.resetmsg(elementid);
			}
		} 
		if(element.attr("nullval")) {
			var nullval = element.attr("nullval");
			var thisid = element.attr("id");
			var seltxt = $(element[0].options[0]).text();
			if(nullval == "")
				nullval = -1;
			if(element.val() == nullval) {
				$.showmsg(elementid, seltxt);
				return false;
			} else {
				$.resetmsg(elementid);
			}
		} 
		if(element.attr("regtype") && (val != "" || element.attr("regtype") == "select")) {
			var tp = element.attr("regtype");
			var flag = false;
			msg = msgs.accept;
			
			if(tp == "email") {
				flag = /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i.test(val);
				msg = msgs.email;
			} else if(tp == "minurl") {
				flag = /^(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(val);
				msg = msgs.minurl;
			} else if(tp == "url") {
				flag = /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(val);
				msg = msgs.url;
			}else if(tp == "num") {
				flag = /^[0-9]+$/i.test(val);
				msg = msgs.num;
			} else if(tp == "mobile") {
				flag = /^((\(\d{2,3}\))|(\d{3}\-))?1(3|5|8)\d{9}$/i.test(val);
				msg = msgs.mobile;
			} else if(tp == "phone") {
				flag = /^((\(\d{2,3}\))|(\d{3}\-))?(\(0\d{2,3}\)|0\d{2,3}-)?[1-9]\d{6,7}(\-\d{1,4})?$/i.test(val);
				msg = msgs.phone;
			} else if(tp == "mobilephone") {
				flag = /^((\(\d{2,3}\))|(\d{3}\-))?(\(0\d{2,3}\)|0\d{2,3}-)?[1-9]\d{6,7}(\-\d{1,4})?$/i.test(val);
				if(!flag)
					flag = /^((\(\d{2,3}\))|(\d{3}\-))?1(3|5|8)\d{9}$/i.test(val);
				msg = msgs.fullphone;
			} else if(tp == "select") {
				var thisval = element.val();
				var verifyval = $(element[0].options[0]).val();
				flag = thisval != verifyval;
				msg = $(element[0].options[0]).text();
			}
			if(!flag) {
				$.showmsg(elementid, $.format(msg));
				return false;
			} else {
				$.resetmsg(elementid);
			}
		}
		if(element.attr("range")) {
			var range = element.attr("range");
			range = range.split("-");
			if(val.length < range[0] || val.length > range[1]) {
				$.showmsg(elementid, $.format(msgs.range, range));
				return false;
			} else {
				$.resetmsg(elementid);
			}
		} 
		if(element.attr("regex") && val != "") {
			var regex = element.attr("regex");
			if(!eval(regex).exec(val)) {
				$.showmsg(elementid, $.format(msgs.accept));
				return false;
			} else {
				$.resetmsg(elementid);
			}
		} 
		if(element.attr("equalTo")) {
			var equalTo = element.attr("equalTo");
			var repeat = $("#"+equalTo).val();
			if(repeat != val) {
				$.showmsg(elementid, $.format(msgs.equalTo));
				return false;
			} else {
				$.resetmsg(elementid);
			}
		}
		if(element.attr("ajax")) {
			var url = element.attr("ajax")+"&"+element.attr("id")+"="+encodeURIComponent(encodeURIComponent(val));
			$.get(url, function(data){
				if(data.replace(/(^\s*)|(\s*$)/g, "") != "") {
					$.showmsg(elementid, data);
					return false;
				}
			});
		}
		errelement.remove();
	}
	
	var msgs = config.msgs;
	var formid = $(this).attr("id");
	$("#"+formid+" input[id], #"+formid+" textarea[id], #"+formid+" select[id]").bind("blur", function(){
		var elementid = $(this).attr("id");
		$.validateElement(elementid);
	});
	validate_submitfun = function(){
		$("#"+formid+" input[id], #"+formid+" textarea[id], #"+formid+" select[id]").each(function(){
			var elementid = $(this).attr("id");
			$.validateElement(elementid, 2);
			//$(this).blur();
		});
		var errlr = $("#"+formid+" "+config.errel+"[name='luc_error_msg']");
		
		if(errlr.length > 0) {
			var errcon = $(errlr[0]).html();
			alert(errcon);
			if($(errlr[0]).prev("input[id]"))
				$(errlr[0]).prev("input[id]").focus();
			return false;
		}
		var flag = config.callback();
		if(typeof(flag) == "boolean" && !flag) {
			return flag;
		}
		return true;
	}
	
	$.getValidatelusConfig = function(name) {
		if(eval("config."+name))
			return eval("config."+name);
		else
			return "";
	}
	
	if(config.submittype == "auto") {
		$(this).bind("submit", validate_submitfun);
	} else {
		$(this).bind("submit", function(){
			validate_submitfun;
			return false;
		});
	}
};

function validateform(formid) {
	$("#"+formid+" input[id], #"+formid+" textarea[id], #"+formid+" select[id]").each(function(){
		var elementid = $(this).attr("id");
		$.validateElement(elementid, 2);
		//$(this).blur();
	});
	var errlr = $("#"+formid+" "+$.getValidatelusConfig("errel")+"[name='luc_error_msg']");
	if(errlr.length > 0) {
		var errcon = $(errlr[0]).html();
		alert(errcon);
		if($(errlr[0]).prev("input[id]"))
			$(errlr[0]).prev("input[id]").focus();
		return false;
	}
	return true;
}