(function($){let ID='hwt';let HighlightWithinTextarea=function($el,config){this.init($el,config);};HighlightWithinTextarea.prototype={init:function($el,config){this.$el=$el;if(this.getType(config)==='function'){config={highlight:config};}
if(this.getType(config)==='custom'){this.highlight=config;this.generate();}else{console.error('valid config object not provided');}},getType:function(instance){let type=typeof instance;if(!instance){return'falsey';}else if(Array.isArray(instance)){if(instance.length===2&&typeof instance[0]==='number'&&typeof instance[1]==='number'){return'range';}else{return'array';}}else if(type==='object'){if(instance instanceof RegExp){return'regexp';}else if(instance.hasOwnProperty('highlight')){return'custom';}}else if(type==='function'||type==='string'){return type;}
return'other';},generate:function(){this.$el.addClass(ID+'-input '+ID+'-content').on('input.'+ID,this.handleInput.bind(this)).on('scroll.'+ID,this.handleScroll.bind(this));this.$highlights=$('<div>',{class:ID+'-highlights '+ID+'-content'});this.$backdrop=$('<div>',{class:ID+'-backdrop'}).append(this.$highlights);this.$container=$('<div>',{class:ID+'-container'}).insertAfter(this.$el).append(this.$backdrop,this.$el).on('scroll',this.blockContainerScroll.bind(this));this.browser=this.detectBrowser();switch(this.browser){case'firefox':this.fixFirefox();break;case'ios':this.fixIOS();break;}
this.isGenerated=true;this.handleInput();},detectBrowser:function(){let ua=window.navigator.userAgent.toLowerCase();if(ua.indexOf('firefox')!==-1){return'firefox';}else if(!!ua.match(/msie|trident\/7|edge/)){return'ie';}else if(!!ua.match(/ipad|iphone|ipod/)&&ua.indexOf('windows phone')===-1){return'ios';}else{return'other';}},fixFirefox:function(){let padding=this.$highlights.css(['padding-top','padding-right','padding-bottom','padding-left']);let border=this.$highlights.css(['border-top-width','border-right-width','border-bottom-width','border-left-width']);this.$highlights.css({'padding':'0','border-width':'0'});this.$backdrop.css({'margin-top':'+='+padding['padding-top'],'margin-right':'+='+padding['padding-right'],'margin-bottom':'+='+padding['padding-bottom'],'margin-left':'+='+padding['padding-left'],}).css({'margin-top':'+='+border['border-top-width'],'margin-right':'+='+border['border-right-width'],'margin-bottom':'+='+border['border-bottom-width'],'margin-left':'+='+border['border-left-width'],});},fixIOS:function(){this.$highlights.css({'padding-left':'+=3px','padding-right':'+=3px'});},handleInput:function(){let input=this.$el.val();let ranges=this.getRanges(input,this.highlight);let unstaggeredRanges=this.removeStaggeredRanges(ranges);let boundaries=this.getBoundaries(unstaggeredRanges);this.renderMarks(boundaries);},getRanges:function(input,highlight){let type=this.getType(highlight);switch(type){case'array':return this.getArrayRanges(input,highlight);case'function':return this.getFunctionRanges(input,highlight);case'regexp':return this.getRegExpRanges(input,highlight);case'string':return this.getStringRanges(input,highlight);case'range':return this.getRangeRanges(input,highlight);case'custom':return this.getCustomRanges(input,highlight);default:if(!highlight){return[];}else{console.error('unrecognized highlight type');}}},getArrayRanges:function(input,arr){let ranges=arr.map(this.getRanges.bind(this,input));return Array.prototype.concat.apply([],ranges);},getFunctionRanges:function(input,func){return this.getRanges(input,func(input));},getRegExpRanges:function(input,regex){let ranges=[];let match;while(match=regex.exec(input),match!==null){ranges.push([match.index,match.index+match[0].length]);if(!regex.global){break;}}
return ranges;},getStringRanges:function(input,str){let ranges=[];let inputLower=input.toLowerCase();let strLower=str.toLowerCase();let index=0;while(index=inputLower.indexOf(strLower,index),index!==-1){ranges.push([index,index+strLower.length]);index+=strLower.length;}
return ranges;},getRangeRanges:function(input,range){return[range];},getCustomRanges:function(input,custom){let ranges=this.getRanges(input,custom.highlight);if(custom.className){ranges.forEach(function(range){if(range.className){range.className=custom.className+' '+range.className;}else{range.className=custom.className;}});}
return ranges;},removeStaggeredRanges:function(ranges){let unstaggeredRanges=[];ranges.forEach(function(range){let isStaggered=unstaggeredRanges.some(function(unstaggeredRange){let isStartInside=range[0]>unstaggeredRange[0]&&range[0]<unstaggeredRange[1];let isStopInside=range[1]>unstaggeredRange[0]&&range[1]<unstaggeredRange[1];return isStartInside!==isStopInside;});if(!isStaggered){unstaggeredRanges.push(range);}});return unstaggeredRanges;},getBoundaries:function(ranges){let boundaries=[];ranges.forEach(function(range){boundaries.push({type:'start',index:range[0],className:range.className});boundaries.push({type:'stop',index:range[1]});});this.sortBoundaries(boundaries);return boundaries;},sortBoundaries:function(boundaries){boundaries.sort(function(a,b){if(a.index!==b.index){return b.index-a.index;}else if(a.type==='stop'&&b.type==='start'){return 1;}else if(a.type==='start'&&b.type==='stop'){return-1;}else{return 0;}});},renderMarks:function(boundaries){let input=this.$el.val();boundaries.forEach(function(boundary){let markup;if(boundary.type==='stop'){markup='</mark>';}else if(boundary.className){markup='<mark class="'+boundary.className+'">';}else{markup='<mark>';}
input=input.slice(0,boundary.index)+markup+input.slice(boundary.index);});input=input.replace(/\n(<\/mark>)?$/,'\n\n$1');if(this.browser==='ie'){input=input.replace(/ /g,' <wbr>').replace(/<mark <wbr>/g,'<mark ');}
this.$highlights.html(input);},handleScroll:function(){let scrollTop=this.$el.scrollTop();this.$backdrop.scrollTop(scrollTop);let scrollLeft=this.$el.scrollLeft();this.$backdrop.css('transform',(scrollLeft>0)?'translateX('+-scrollLeft+'px)':'');},blockContainerScroll:function(){this.$container.scrollLeft(0);},destroy:function(){this.$backdrop.remove();this.$el.unwrap().removeClass(ID+'-text '+ID+'-input').off(ID).removeData(ID);},};$.fn.highlightWithinTextarea=function(options){return this.each(function(){let $this=$(this);let plugin=$this.data(ID);if(typeof options==='string'){if(plugin){switch(options){case'update':plugin.handleInput();break;case'destroy':plugin.destroy();break;default:console.error('unrecognized method string');}}else{console.error('plugin must be instantiated first');}}else{if(plugin){plugin.destroy();}
plugin=new HighlightWithinTextarea($this,options);if(plugin.isGenerated){$this.data(ID,plugin);}}});};})(jQuery);+function($){'use strict';function transitionEnd(){var el=document.createElement('bootstrap')
var transEndEventNames={WebkitTransition:'webkitTransitionEnd',MozTransition:'transitionend',OTransition:'oTransitionEnd otransitionend',transition:'transitionend'}
for(var name in transEndEventNames){if(el.style[name]!==undefined){return{end:transEndEventNames[name]}}}
return false}
$.fn.emulateTransitionEnd=function(duration){var called=false
var $el=this
$(this).one('bsTransitionEnd',function(){called=true})
var callback=function(){if(!called)$($el).trigger($.support.transition.end)}
setTimeout(callback,duration)
return this}
$(function(){$.support.transition=transitionEnd()
if(!$.support.transition)return
$.event.special.bsTransitionEnd={bindType:$.support.transition.end,delegateType:$.support.transition.end,handle:function(e){if($(e.target).is(this))return e.handleObj.handler.apply(this,arguments)}}})}(jQuery);+function($){'use strict';var Collapse=function(element,options){this.$element=$(element)
this.options=$.extend({},Collapse.DEFAULTS,options)
this.$trigger=$('[data-toggle="collapse"][href="#'+element.id+'"],'+
'[data-toggle="collapse"][data-target="#'+element.id+'"]')
this.transitioning=null
if(this.options.parent){this.$parent=this.getParent()}else{this.addAriaAndCollapsedClass(this.$element,this.$trigger)}
if(this.options.toggle)this.toggle()}
Collapse.VERSION='3.3.7'
Collapse.TRANSITION_DURATION=350
Collapse.DEFAULTS={toggle:true}
Collapse.prototype.dimension=function(){var hasWidth=this.$element.hasClass('width')
return hasWidth?'width':'height'}
Collapse.prototype.show=function(){if(this.transitioning||this.$element.hasClass('in'))return
var activesData
var actives=this.$parent&&this.$parent.children('.panel').children('.in, .collapsing')
if(actives&&actives.length){activesData=actives.data('bs.collapse')
if(activesData&&activesData.transitioning)return}
var startEvent=$.Event('show.bs.collapse')
this.$element.trigger(startEvent)
if(startEvent.isDefaultPrevented())return
if(actives&&actives.length){Plugin.call(actives,'hide')
activesData||actives.data('bs.collapse',null)}
var dimension=this.dimension()
this.$element.removeClass('collapse').addClass('collapsing')[dimension](0).attr('aria-expanded',true)
this.$trigger.removeClass('collapsed').attr('aria-expanded',true)
this.transitioning=1
var complete=function(){this.$element.removeClass('collapsing').addClass('collapse in')[dimension]('')
this.transitioning=0
this.$element.trigger('shown.bs.collapse')}
if(!$.support.transition)return complete.call(this)
var scrollSize=$.camelCase(['scroll',dimension].join('-'))
this.$element.one('bsTransitionEnd',$.proxy(complete,this)).emulateTransitionEnd(Collapse.TRANSITION_DURATION)[dimension](this.$element[0][scrollSize])}
Collapse.prototype.hide=function(){if(this.transitioning||!this.$element.hasClass('in'))return
var startEvent=$.Event('hide.bs.collapse')
this.$element.trigger(startEvent)
if(startEvent.isDefaultPrevented())return
var dimension=this.dimension()
this.$element[dimension](this.$element[dimension]())[0].offsetHeight
this.$element.addClass('collapsing').removeClass('collapse in').attr('aria-expanded',false)
this.$trigger.addClass('collapsed').attr('aria-expanded',false)
this.transitioning=1
var complete=function(){this.transitioning=0
this.$element.removeClass('collapsing').addClass('collapse').trigger('hidden.bs.collapse')}
if(!$.support.transition)return complete.call(this)
this.$element
[dimension](0).one('bsTransitionEnd',$.proxy(complete,this)).emulateTransitionEnd(Collapse.TRANSITION_DURATION)}
Collapse.prototype.toggle=function(){this[this.$element.hasClass('in')?'hide':'show']()}
Collapse.prototype.getParent=function(){return $(this.options.parent).find('[data-toggle="collapse"][data-parent="'+this.options.parent+'"]').each($.proxy(function(i,element){var $element=$(element)
this.addAriaAndCollapsedClass(getTargetFromTrigger($element),$element)},this)).end()}
Collapse.prototype.addAriaAndCollapsedClass=function($element,$trigger){var isOpen=$element.hasClass('in')
$element.attr('aria-expanded',isOpen)
$trigger.toggleClass('collapsed',!isOpen).attr('aria-expanded',isOpen)}
function getTargetFromTrigger($trigger){var href
var target=$trigger.attr('data-target')||(href=$trigger.attr('href'))&&href.replace(/.*(?=#[^\s]+$)/,'')
return $(target)}
function Plugin(option){return this.each(function(){var $this=$(this)
var data=$this.data('bs.collapse')
var options=$.extend({},Collapse.DEFAULTS,$this.data(),typeof option=='object'&&option)
if(!data&&options.toggle&&/show|hide/.test(option))options.toggle=false
if(!data)$this.data('bs.collapse',(data=new Collapse(this,options)))
if(typeof option=='string')data[option]()})}
var old=$.fn.collapse
$.fn.collapse=Plugin
$.fn.collapse.Constructor=Collapse
$.fn.collapse.noConflict=function(){$.fn.collapse=old
return this}
$(document).on('click.bs.collapse.data-api','[data-toggle="collapse"]',function(e){var $this=$(this)
if(!$this.attr('data-target'))e.preventDefault()
var $target=getTargetFromTrigger($this)
var data=$target.data('bs.collapse')
var option=data?'toggle':$this.data()
Plugin.call($target,option)})}(jQuery);﻿/*! version : 4.17.47
 =========================================================
 bootstrap-datetimejs
 https://github.com/Eonasdan/bootstrap-datetimepicker
 Copyright (c) 2015 Jonathan Peterson
 =========================================================
 */

(function(factory){'use strict';if(typeof define==='function'&&define.amd){define(['jquery','moment'],factory);}else if(typeof exports==='object'){module.exports=factory(require('jquery'),require('moment'));}else{if(typeof jQuery==='undefined'){throw'bootstrap-datetimepicker requires jQuery to be loaded first';}
if(typeof moment==='undefined'){throw'bootstrap-datetimepicker requires Moment.js to be loaded first';}
factory(jQuery,moment);}}(function($,moment){'use strict';if(!moment){throw new Error('bootstrap-datetimepicker requires Moment.js to be loaded first');}
var dateTimePicker=function(element,options){var picker={},date,viewDate,unset=true,input,component=false,widget=false,use24Hours,minViewModeNumber=0,actualFormat,parseFormats,currentViewMode,datePickerModes=[{clsName:'days',navFnc:'M',navStep:1},{clsName:'months',navFnc:'y',navStep:1},{clsName:'years',navFnc:'y',navStep:10},{clsName:'decades',navFnc:'y',navStep:100}],viewModes=['days','months','years','decades'],verticalModes=['top','bottom','auto'],horizontalModes=['left','right','auto'],toolbarPlacements=['default','top','bottom'],keyMap={'up':38,38:'up','down':40,40:'down','left':37,37:'left','right':39,39:'right','tab':9,9:'tab','escape':27,27:'escape','enter':13,13:'enter','pageUp':33,33:'pageUp','pageDown':34,34:'pageDown','shift':16,16:'shift','control':17,17:'control','space':32,32:'space','t':84,84:'t','delete':46,46:'delete'},keyState={},hasTimeZone=function(){return moment.tz!==undefined&&options.timeZone!==undefined&&options.timeZone!==null&&options.timeZone!=='';},getMoment=function(d){var returnMoment;if(d===undefined||d===null){returnMoment=moment();}else if(moment.isDate(d)||moment.isMoment(d)){returnMoment=moment(d);}else if(hasTimeZone()){returnMoment=moment.tz(d,parseFormats,options.useStrict,options.timeZone);}else{returnMoment=moment(d,parseFormats,options.useStrict);}
if(hasTimeZone()){returnMoment.tz(options.timeZone);}
return returnMoment;},isEnabled=function(granularity){if(typeof granularity!=='string'||granularity.length>1){throw new TypeError('isEnabled expects a single character string parameter');}
switch(granularity){case'y':return actualFormat.indexOf('Y')!==-1;case'M':return actualFormat.indexOf('M')!==-1;case'd':return actualFormat.toLowerCase().indexOf('d')!==-1;case'h':case'H':return actualFormat.toLowerCase().indexOf('h')!==-1;case'm':return actualFormat.indexOf('m')!==-1;case's':return actualFormat.indexOf('s')!==-1;default:return false;}},hasTime=function(){return(isEnabled('h')||isEnabled('m')||isEnabled('s'));},hasDate=function(){return(isEnabled('y')||isEnabled('M')||isEnabled('d'));},getDatePickerTemplate=function(){var headTemplate=$('<thead>').append($('<tr>').append($('<th>').addClass('prev').attr('data-action','previous').append($('<span>').addClass(options.icons.previous))).append($('<th>').addClass('picker-switch').attr('data-action','pickerSwitch').attr('colspan',(options.calendarWeeks?'6':'5'))).append($('<th>').addClass('next').attr('data-action','next').append($('<span>').addClass(options.icons.next)))),contTemplate=$('<tbody>').append($('<tr>').append($('<td>').attr('colspan',(options.calendarWeeks?'8':'7'))));return[$('<div>').addClass('datepicker-days').append($('<table>').addClass('table-condensed').append(headTemplate).append($('<tbody>'))),$('<div>').addClass('datepicker-months').append($('<table>').addClass('table-condensed').append(headTemplate.clone()).append(contTemplate.clone())),$('<div>').addClass('datepicker-years').append($('<table>').addClass('table-condensed').append(headTemplate.clone()).append(contTemplate.clone())),$('<div>').addClass('datepicker-decades').append($('<table>').addClass('table-condensed').append(headTemplate.clone()).append(contTemplate.clone()))];},getTimePickerMainTemplate=function(){var topRow=$('<tr>'),middleRow=$('<tr>'),bottomRow=$('<tr>');if(isEnabled('h')){topRow.append($('<td>').append($('<a>').attr({href:'#',tabindex:'-1','title':options.tooltips.incrementHour}).addClass('btn').attr('data-action','incrementHours').append($('<span>').addClass(options.icons.up))));middleRow.append($('<td>').append($('<span>').addClass('timepicker-hour').attr({'data-time-component':'hours','title':options.tooltips.pickHour}).attr('data-action','showHours')));bottomRow.append($('<td>').append($('<a>').attr({href:'#',tabindex:'-1','title':options.tooltips.decrementHour}).addClass('btn').attr('data-action','decrementHours').append($('<span>').addClass(options.icons.down))));}
if(isEnabled('m')){if(isEnabled('h')){topRow.append($('<td>').addClass('separator'));middleRow.append($('<td>').addClass('separator').html(':'));bottomRow.append($('<td>').addClass('separator'));}
topRow.append($('<td>').append($('<a>').attr({href:'#',tabindex:'-1','title':options.tooltips.incrementMinute}).addClass('btn').attr('data-action','incrementMinutes').append($('<span>').addClass(options.icons.up))));middleRow.append($('<td>').append($('<span>').addClass('timepicker-minute').attr({'data-time-component':'minutes','title':options.tooltips.pickMinute}).attr('data-action','showMinutes')));bottomRow.append($('<td>').append($('<a>').attr({href:'#',tabindex:'-1','title':options.tooltips.decrementMinute}).addClass('btn').attr('data-action','decrementMinutes').append($('<span>').addClass(options.icons.down))));}
if(isEnabled('s')){if(isEnabled('m')){topRow.append($('<td>').addClass('separator'));middleRow.append($('<td>').addClass('separator').html(':'));bottomRow.append($('<td>').addClass('separator'));}
topRow.append($('<td>').append($('<a>').attr({href:'#',tabindex:'-1','title':options.tooltips.incrementSecond}).addClass('btn').attr('data-action','incrementSeconds').append($('<span>').addClass(options.icons.up))));middleRow.append($('<td>').append($('<span>').addClass('timepicker-second').attr({'data-time-component':'seconds','title':options.tooltips.pickSecond}).attr('data-action','showSeconds')));bottomRow.append($('<td>').append($('<a>').attr({href:'#',tabindex:'-1','title':options.tooltips.decrementSecond}).addClass('btn').attr('data-action','decrementSeconds').append($('<span>').addClass(options.icons.down))));}
if(!use24Hours){topRow.append($('<td>').addClass('separator'));middleRow.append($('<td>').append($('<button>').addClass('btn btn-primary').attr({'data-action':'togglePeriod',tabindex:'-1','title':options.tooltips.togglePeriod})));bottomRow.append($('<td>').addClass('separator'));}
return $('<div>').addClass('timepicker-picker').append($('<table>').addClass('table-condensed').append([topRow,middleRow,bottomRow]));},getTimePickerTemplate=function(){var hoursView=$('<div>').addClass('timepicker-hours').append($('<table>').addClass('table-condensed')),minutesView=$('<div>').addClass('timepicker-minutes').append($('<table>').addClass('table-condensed')),secondsView=$('<div>').addClass('timepicker-seconds').append($('<table>').addClass('table-condensed')),ret=[getTimePickerMainTemplate()];if(isEnabled('h')){ret.push(hoursView);}
if(isEnabled('m')){ret.push(minutesView);}
if(isEnabled('s')){ret.push(secondsView);}
return ret;},getToolbar=function(){var row=[];if(options.showTodayButton){row.push($('<td>').append($('<a>').attr({'data-action':'today','title':options.tooltips.today}).append($('<span>').addClass(options.icons.today))));}
if(!options.sideBySide&&hasDate()&&hasTime()){row.push($('<td>').append($('<a>').attr({'data-action':'togglePicker','title':options.tooltips.selectTime}).append($('<span>').addClass(options.icons.time))));}
if(options.showClear){row.push($('<td>').append($('<a>').attr({'data-action':'clear','title':options.tooltips.clear}).append($('<span>').addClass(options.icons.clear))));}
if(options.showClose){row.push($('<td>').append($('<a>').attr({'data-action':'close','title':options.tooltips.close}).append($('<span>').addClass(options.icons.close))));}
return $('<table>').addClass('table-condensed').append($('<tbody>').append($('<tr>').append(row)));},getTemplate=function(){var template=$('<div>').addClass('bootstrap-datetimepicker-widget dropdown-menu'),dateView=$('<div>').addClass('datepicker').append(getDatePickerTemplate()),timeView=$('<div>').addClass('timepicker').append(getTimePickerTemplate()),content=$('<ul>').addClass('list-unstyled'),toolbar=$('<li>').addClass('picker-switch'+(options.collapse?' accordion-toggle':'')).append(getToolbar());if(options.inline){template.removeClass('dropdown-menu');}
if(use24Hours){template.addClass('usetwentyfour');}
if(isEnabled('s')&&!use24Hours){template.addClass('wider');}
if(options.sideBySide&&hasDate()&&hasTime()){template.addClass('timepicker-sbs');if(options.toolbarPlacement==='top'){template.append(toolbar);}
template.append($('<div>').addClass('row').append(dateView.addClass('col-md-6')).append(timeView.addClass('col-md-6')));if(options.toolbarPlacement==='bottom'){template.append(toolbar);}
return template;}
if(options.toolbarPlacement==='top'){content.append(toolbar);}
if(hasDate()){content.append($('<li>').addClass((options.collapse&&hasTime()?'collapse in':'')).append(dateView));}
if(options.toolbarPlacement==='default'){content.append(toolbar);}
if(hasTime()){content.append($('<li>').addClass((options.collapse&&hasDate()?'collapse':'')).append(timeView));}
if(options.toolbarPlacement==='bottom'){content.append(toolbar);}
return template.append(content);},dataToOptions=function(){var eData,dataOptions={};if(element.is('input')||options.inline){eData=element.data();}else{eData=element.find('input').data();}
if(eData.dateOptions&&eData.dateOptions instanceof Object){dataOptions=$.extend(true,dataOptions,eData.dateOptions);}
$.each(options,function(key){var attributeName='date'+key.charAt(0).toUpperCase()+key.slice(1);if(eData[attributeName]!==undefined){dataOptions[key]=eData[attributeName];}});return dataOptions;},place=function(){var position=(component||element).position(),offset=(component||element).offset(),vertical=options.widgetPositioning.vertical,horizontal=options.widgetPositioning.horizontal,parent;if(options.widgetParent){parent=options.widgetParent.append(widget);}else if(element.is('input')){parent=element.after(widget).parent();}else if(options.inline){parent=element.append(widget);return;}else{parent=element;element.children().first().after(widget);}
if(vertical==='auto'){if(offset.top+widget.height()*1.5>=$(window).height()+$(window).scrollTop()&&widget.height()+element.outerHeight()<offset.top){vertical='top';}else{vertical='bottom';}}
if(horizontal==='auto'){if(parent.width()<offset.left+widget.outerWidth()/2&&offset.left+widget.outerWidth()>$(window).width()){horizontal='right';}else{horizontal='left';}}
if(vertical==='top'){widget.addClass('top').removeClass('bottom');}else{widget.addClass('bottom').removeClass('top');}
if(horizontal==='right'){widget.addClass('pull-right');}else{widget.removeClass('pull-right');}
if(parent.css('position')==='static'){parent=parent.parents().filter(function(){return $(this).css('position')!=='static';}).first();}
if(parent.length===0){throw new Error('datetimepicker component should be placed within a non-static positioned container');}
widget.css({top:vertical==='top'?'auto':position.top+element.outerHeight(),bottom:vertical==='top'?parent.outerHeight()-(parent===element?0:position.top):'auto',left:horizontal==='left'?(parent===element?0:position.left):'auto',right:horizontal==='left'?'auto':parent.outerWidth()-element.outerWidth()-(parent===element?0:position.left)});},notifyEvent=function(e){if(e.type==='dp.change'&&((e.date&&e.date.isSame(e.oldDate))||(!e.date&&!e.oldDate))){return;}
element.trigger(e);},viewUpdate=function(e){if(e==='y'){e='YYYY';}
notifyEvent({type:'dp.update',change:e,viewDate:viewDate.clone()});},showMode=function(dir){if(!widget){return;}
if(dir){currentViewMode=Math.max(minViewModeNumber,Math.min(3,currentViewMode+dir));}
widget.find('.datepicker > div').hide().filter('.datepicker-'+datePickerModes[currentViewMode].clsName).show();},fillDow=function(){var row=$('<tr>'),currentDate=viewDate.clone().startOf('w').startOf('d');if(options.calendarWeeks===true){row.append($('<th>').addClass('cw').text('#'));}
while(currentDate.isBefore(viewDate.clone().endOf('w'))){row.append($('<th>').addClass('dow').text(currentDate.format('dd')));currentDate.add(1,'d');}
widget.find('.datepicker-days thead').append(row);},isInDisabledDates=function(testDate){return options.disabledDates[testDate.format('YYYY-MM-DD')]===true;},isInEnabledDates=function(testDate){return options.enabledDates[testDate.format('YYYY-MM-DD')]===true;},isInDisabledHours=function(testDate){return options.disabledHours[testDate.format('H')]===true;},isInEnabledHours=function(testDate){return options.enabledHours[testDate.format('H')]===true;},isValid=function(targetMoment,granularity){if(!targetMoment.isValid()){return false;}
if(options.disabledDates&&granularity==='d'&&isInDisabledDates(targetMoment)){return false;}
if(options.enabledDates&&granularity==='d'&&!isInEnabledDates(targetMoment)){return false;}
if(options.minDate&&targetMoment.isBefore(options.minDate,granularity)){return false;}
if(options.maxDate&&targetMoment.isAfter(options.maxDate,granularity)){return false;}
if(options.daysOfWeekDisabled&&granularity==='d'&&options.daysOfWeekDisabled.indexOf(targetMoment.day())!==-1){return false;}
if(options.disabledHours&&(granularity==='h'||granularity==='m'||granularity==='s')&&isInDisabledHours(targetMoment)){return false;}
if(options.enabledHours&&(granularity==='h'||granularity==='m'||granularity==='s')&&!isInEnabledHours(targetMoment)){return false;}
if(options.disabledTimeIntervals&&(granularity==='h'||granularity==='m'||granularity==='s')){var found=false;$.each(options.disabledTimeIntervals,function(){if(targetMoment.isBetween(this[0],this[1])){found=true;return false;}});if(found){return false;}}
return true;},fillMonths=function(){var spans=[],monthsShort=viewDate.clone().startOf('y').startOf('d');while(monthsShort.isSame(viewDate,'y')){spans.push($('<span>').attr('data-action','selectMonth').addClass('month').text(monthsShort.format('MMM')));monthsShort.add(1,'M');}
widget.find('.datepicker-months td').empty().append(spans);},updateMonths=function(){var monthsView=widget.find('.datepicker-months'),monthsViewHeader=monthsView.find('th'),months=monthsView.find('tbody').find('span');monthsViewHeader.eq(0).find('span').attr('title',options.tooltips.prevYear);monthsViewHeader.eq(1).attr('title',options.tooltips.selectYear);monthsViewHeader.eq(2).find('span').attr('title',options.tooltips.nextYear);monthsView.find('.disabled').removeClass('disabled');if(!isValid(viewDate.clone().subtract(1,'y'),'y')){monthsViewHeader.eq(0).addClass('disabled');}
monthsViewHeader.eq(1).text(viewDate.year());if(!isValid(viewDate.clone().add(1,'y'),'y')){monthsViewHeader.eq(2).addClass('disabled');}
months.removeClass('active');if(date.isSame(viewDate,'y')&&!unset){months.eq(date.month()).addClass('active');}
months.each(function(index){if(!isValid(viewDate.clone().month(index),'M')){$(this).addClass('disabled');}});},updateYears=function(){var yearsView=widget.find('.datepicker-years'),yearsViewHeader=yearsView.find('th'),startYear=viewDate.clone().subtract(5,'y'),endYear=viewDate.clone().add(6,'y'),html='';yearsViewHeader.eq(0).find('span').attr('title',options.tooltips.prevDecade);yearsViewHeader.eq(1).attr('title',options.tooltips.selectDecade);yearsViewHeader.eq(2).find('span').attr('title',options.tooltips.nextDecade);yearsView.find('.disabled').removeClass('disabled');if(options.minDate&&options.minDate.isAfter(startYear,'y')){yearsViewHeader.eq(0).addClass('disabled');}
yearsViewHeader.eq(1).text(startYear.year()+'-'+endYear.year());if(options.maxDate&&options.maxDate.isBefore(endYear,'y')){yearsViewHeader.eq(2).addClass('disabled');}
while(!startYear.isAfter(endYear,'y')){html+='<span data-action="selectYear" class="year'+(startYear.isSame(date,'y')&&!unset?' active':'')+(!isValid(startYear,'y')?' disabled':'')+'">'+startYear.year()+'</span>';startYear.add(1,'y');}
yearsView.find('td').html(html);},updateDecades=function(){var decadesView=widget.find('.datepicker-decades'),decadesViewHeader=decadesView.find('th'),startDecade=moment({y:viewDate.year()-(viewDate.year()%100)-1}),endDecade=startDecade.clone().add(100,'y'),startedAt=startDecade.clone(),minDateDecade=false,maxDateDecade=false,endDecadeYear,html='';decadesViewHeader.eq(0).find('span').attr('title',options.tooltips.prevCentury);decadesViewHeader.eq(2).find('span').attr('title',options.tooltips.nextCentury);decadesView.find('.disabled').removeClass('disabled');if(startDecade.isSame(moment({y:1900}))||(options.minDate&&options.minDate.isAfter(startDecade,'y'))){decadesViewHeader.eq(0).addClass('disabled');}
decadesViewHeader.eq(1).text(startDecade.year()+'-'+endDecade.year());if(startDecade.isSame(moment({y:2000}))||(options.maxDate&&options.maxDate.isBefore(endDecade,'y'))){decadesViewHeader.eq(2).addClass('disabled');}
while(!startDecade.isAfter(endDecade,'y')){endDecadeYear=startDecade.year()+12;minDateDecade=options.minDate&&options.minDate.isAfter(startDecade,'y')&&options.minDate.year()<=endDecadeYear;maxDateDecade=options.maxDate&&options.maxDate.isAfter(startDecade,'y')&&options.maxDate.year()<=endDecadeYear;html+='<span data-action="selectDecade" class="decade'+(date.isAfter(startDecade)&&date.year()<=endDecadeYear?' active':'')+
(!isValid(startDecade,'y')&&!minDateDecade&&!maxDateDecade?' disabled':'')+'" data-selection="'+(startDecade.year()+6)+'">'+(startDecade.year()+1)+' - '+(startDecade.year()+12)+'</span>';startDecade.add(12,'y');}
html+='<span></span><span></span><span></span>';decadesView.find('td').html(html);decadesViewHeader.eq(1).text((startedAt.year()+1)+'-'+(startDecade.year()));},fillDate=function(){var daysView=widget.find('.datepicker-days'),daysViewHeader=daysView.find('th'),currentDate,html=[],row,clsNames=[],i;if(!hasDate()){return;}
daysViewHeader.eq(0).find('span').attr('title',options.tooltips.prevMonth);daysViewHeader.eq(1).attr('title',options.tooltips.selectMonth);daysViewHeader.eq(2).find('span').attr('title',options.tooltips.nextMonth);daysView.find('.disabled').removeClass('disabled');daysViewHeader.eq(1).text(viewDate.format(options.dayViewHeaderFormat));if(!isValid(viewDate.clone().subtract(1,'M'),'M')){daysViewHeader.eq(0).addClass('disabled');}
if(!isValid(viewDate.clone().add(1,'M'),'M')){daysViewHeader.eq(2).addClass('disabled');}
currentDate=viewDate.clone().startOf('M').startOf('w').startOf('d');for(i=0;i<42;i++){if(currentDate.weekday()===0){row=$('<tr>');if(options.calendarWeeks){row.append('<td class="cw">'+currentDate.week()+'</td>');}
html.push(row);}
clsNames=['day'];if(currentDate.isBefore(viewDate,'M')){clsNames.push('old');}
if(currentDate.isAfter(viewDate,'M')){clsNames.push('new');}
if(currentDate.isSame(date,'d')&&!unset){clsNames.push('active');}
if(!isValid(currentDate,'d')){clsNames.push('disabled');}
if(currentDate.isSame(getMoment(),'d')){clsNames.push('today');}
if(currentDate.day()===0||currentDate.day()===6){clsNames.push('weekend');}
notifyEvent({type:'dp.classify',date:currentDate,classNames:clsNames});row.append('<td data-action="selectDay" data-day="'+currentDate.format('L')+'" class="'+clsNames.join(' ')+'">'+currentDate.date()+'</td>');currentDate.add(1,'d');}
daysView.find('tbody').empty().append(html);updateMonths();updateYears();updateDecades();},fillHours=function(){var table=widget.find('.timepicker-hours table'),currentHour=viewDate.clone().startOf('d'),html=[],row=$('<tr>');if(viewDate.hour()>11&&!use24Hours){currentHour.hour(12);}
while(currentHour.isSame(viewDate,'d')&&(use24Hours||(viewDate.hour()<12&&currentHour.hour()<12)||viewDate.hour()>11)){if(currentHour.hour()%4===0){row=$('<tr>');html.push(row);}
row.append('<td data-action="selectHour" class="hour'+(!isValid(currentHour,'h')?' disabled':'')+'">'+currentHour.format(use24Hours?'HH':'hh')+'</td>');currentHour.add(1,'h');}
table.empty().append(html);},fillMinutes=function(){var table=widget.find('.timepicker-minutes table'),currentMinute=viewDate.clone().startOf('h'),html=[],row=$('<tr>'),step=options.stepping===1?5:options.stepping;while(viewDate.isSame(currentMinute,'h')){if(currentMinute.minute()%(step*4)===0){row=$('<tr>');html.push(row);}
row.append('<td data-action="selectMinute" class="minute'+(!isValid(currentMinute,'m')?' disabled':'')+'">'+currentMinute.format('mm')+'</td>');currentMinute.add(step,'m');}
table.empty().append(html);},fillSeconds=function(){var table=widget.find('.timepicker-seconds table'),currentSecond=viewDate.clone().startOf('m'),html=[],row=$('<tr>');while(viewDate.isSame(currentSecond,'m')){if(currentSecond.second()%20===0){row=$('<tr>');html.push(row);}
row.append('<td data-action="selectSecond" class="second'+(!isValid(currentSecond,'s')?' disabled':'')+'">'+currentSecond.format('ss')+'</td>');currentSecond.add(5,'s');}
table.empty().append(html);},fillTime=function(){var toggle,newDate,timeComponents=widget.find('.timepicker span[data-time-component]');if(!use24Hours){toggle=widget.find('.timepicker [data-action=togglePeriod]');newDate=date.clone().add((date.hours()>=12)?-12:12,'h');toggle.text(date.format('A'));if(isValid(newDate,'h')){toggle.removeClass('disabled');}else{toggle.addClass('disabled');}}
timeComponents.filter('[data-time-component=hours]').text(date.format(use24Hours?'HH':'hh'));timeComponents.filter('[data-time-component=minutes]').text(date.format('mm'));timeComponents.filter('[data-time-component=seconds]').text(date.format('ss'));fillHours();fillMinutes();fillSeconds();},update=function(){if(!widget){return;}
fillDate();fillTime();},setValue=function(targetMoment){var oldDate=unset?null:date;if(!targetMoment){unset=true;input.val('');element.data('date','');notifyEvent({type:'dp.change',date:false,oldDate:oldDate});update();return;}
targetMoment=targetMoment.clone().locale(options.locale);if(hasTimeZone()){targetMoment.tz(options.timeZone);}
if(options.stepping!==1){targetMoment.minutes((Math.round(targetMoment.minutes()/options.stepping)*options.stepping)).seconds(0);while(options.minDate&&targetMoment.isBefore(options.minDate)){targetMoment.add(options.stepping,'minutes');}}
if(isValid(targetMoment)){date=targetMoment;viewDate=date.clone();input.val(date.format(actualFormat));element.data('date',date.format(actualFormat));unset=false;update();notifyEvent({type:'dp.change',date:date.clone(),oldDate:oldDate});}else{if(!options.keepInvalid){input.val(unset?'':date.format(actualFormat));}else{notifyEvent({type:'dp.change',date:targetMoment,oldDate:oldDate});}
notifyEvent({type:'dp.error',date:targetMoment,oldDate:oldDate});}},hide=function(){var transitioning=false;if(!widget){return picker;}
widget.find('.collapse').each(function(){var collapseData=$(this).data('collapse');if(collapseData&&collapseData.transitioning){transitioning=true;return false;}
return true;});if(transitioning){return picker;}
if(component&&component.hasClass('btn')){component.toggleClass('active');}
widget.hide();$(window).off('resize',place);widget.off('click','[data-action]');widget.off('mousedown',false);widget.remove();widget=false;notifyEvent({type:'dp.hide',date:date.clone()});input.blur();viewDate=date.clone();return picker;},clear=function(){setValue(null);},parseInputDate=function(inputDate){if(options.parseInputDate===undefined){if(!moment.isMoment(inputDate)||inputDate instanceof Date){inputDate=getMoment(inputDate);}}else{inputDate=options.parseInputDate(inputDate);}
return inputDate;},actions={next:function(){var navFnc=datePickerModes[currentViewMode].navFnc;viewDate.add(datePickerModes[currentViewMode].navStep,navFnc);fillDate();viewUpdate(navFnc);},previous:function(){var navFnc=datePickerModes[currentViewMode].navFnc;viewDate.subtract(datePickerModes[currentViewMode].navStep,navFnc);fillDate();viewUpdate(navFnc);},pickerSwitch:function(){showMode(1);},selectMonth:function(e){var month=$(e.target).closest('tbody').find('span').index($(e.target));viewDate.month(month);if(currentViewMode===minViewModeNumber){setValue(date.clone().year(viewDate.year()).month(viewDate.month()));if(!options.inline){hide();}}else{showMode(-1);fillDate();}
viewUpdate('M');},selectYear:function(e){var year=parseInt($(e.target).text(),10)||0;viewDate.year(year);if(currentViewMode===minViewModeNumber){setValue(date.clone().year(viewDate.year()));if(!options.inline){hide();}}else{showMode(-1);fillDate();}
viewUpdate('YYYY');},selectDecade:function(e){var year=parseInt($(e.target).data('selection'),10)||0;viewDate.year(year);if(currentViewMode===minViewModeNumber){setValue(date.clone().year(viewDate.year()));if(!options.inline){hide();}}else{showMode(-1);fillDate();}
viewUpdate('YYYY');},selectDay:function(e){var day=viewDate.clone();if($(e.target).is('.old')){day.subtract(1,'M');}
if($(e.target).is('.new')){day.add(1,'M');}
setValue(day.date(parseInt($(e.target).text(),10)));if(!hasTime()&&!options.keepOpen&&!options.inline){hide();}},incrementHours:function(){var newDate=date.clone().add(1,'h');if(isValid(newDate,'h')){setValue(newDate);}},incrementMinutes:function(){var newDate=date.clone().add(options.stepping,'m');if(isValid(newDate,'m')){setValue(newDate);}},incrementSeconds:function(){var newDate=date.clone().add(1,'s');if(isValid(newDate,'s')){setValue(newDate);}},decrementHours:function(){var newDate=date.clone().subtract(1,'h');if(isValid(newDate,'h')){setValue(newDate);}},decrementMinutes:function(){var newDate=date.clone().subtract(options.stepping,'m');if(isValid(newDate,'m')){setValue(newDate);}},decrementSeconds:function(){var newDate=date.clone().subtract(1,'s');if(isValid(newDate,'s')){setValue(newDate);}},togglePeriod:function(){setValue(date.clone().add((date.hours()>=12)?-12:12,'h'));},togglePicker:function(e){var $this=$(e.target),$parent=$this.closest('ul'),expanded=$parent.find('.in'),closed=$parent.find('.collapse:not(.in)'),collapseData;if(expanded&&expanded.length){collapseData=expanded.data('collapse');if(collapseData&&collapseData.transitioning){return;}
if(expanded.collapse){expanded.collapse('hide');closed.collapse('show');}else{expanded.removeClass('in');closed.addClass('in');}
if($this.is('span')){$this.toggleClass(options.icons.time+' '+options.icons.date);}else{$this.find('span').toggleClass(options.icons.time+' '+options.icons.date);}
}},showPicker:function(){widget.find('.timepicker > div:not(.timepicker-picker)').hide();widget.find('.timepicker .timepicker-picker').show();},showHours:function(){widget.find('.timepicker .timepicker-picker').hide();widget.find('.timepicker .timepicker-hours').show();},showMinutes:function(){widget.find('.timepicker .timepicker-picker').hide();widget.find('.timepicker .timepicker-minutes').show();},showSeconds:function(){widget.find('.timepicker .timepicker-picker').hide();widget.find('.timepicker .timepicker-seconds').show();},selectHour:function(e){var hour=parseInt($(e.target).text(),10);if(!use24Hours){if(date.hours()>=12){if(hour!==12){hour+=12;}}else{if(hour===12){hour=0;}}}
setValue(date.clone().hours(hour));actions.showPicker.call(picker);},selectMinute:function(e){setValue(date.clone().minutes(parseInt($(e.target).text(),10)));actions.showPicker.call(picker);},selectSecond:function(e){setValue(date.clone().seconds(parseInt($(e.target).text(),10)));actions.showPicker.call(picker);},clear:clear,today:function(){var todaysDate=getMoment();if(isValid(todaysDate,'d')){setValue(todaysDate);}},close:hide},doAction=function(e){if($(e.currentTarget).is('.disabled')){return false;}
actions[$(e.currentTarget).data('action')].apply(picker,arguments);return false;},show=function(){var currentMoment,useCurrentGranularity={'year':function(m){return m.month(0).date(1).hours(0).seconds(0).minutes(0);},'month':function(m){return m.date(1).hours(0).seconds(0).minutes(0);},'day':function(m){return m.hours(0).seconds(0).minutes(0);},'hour':function(m){return m.seconds(0).minutes(0);},'minute':function(m){return m.seconds(0);}};if(input.prop('disabled')||(!options.ignoreReadonly&&input.prop('readonly'))||widget){return picker;}
if(input.val()!==undefined&&input.val().trim().length!==0){setValue(parseInputDate(input.val().trim()));}else if(unset&&options.useCurrent&&(options.inline||(input.is('input')&&input.val().trim().length===0))){currentMoment=getMoment();if(typeof options.useCurrent==='string'){currentMoment=useCurrentGranularity[options.useCurrent](currentMoment);}
setValue(currentMoment);}
widget=getTemplate();fillDow();fillMonths();widget.find('.timepicker-hours').hide();widget.find('.timepicker-minutes').hide();widget.find('.timepicker-seconds').hide();update();showMode();$(window).on('resize',place);widget.on('click','[data-action]',doAction);widget.on('mousedown',false);if(component&&component.hasClass('btn')){component.toggleClass('active');}
place();widget.show();if(options.focusOnShow&&!input.is(':focus')){input.focus();}
notifyEvent({type:'dp.show'});return picker;},toggle=function(){return(widget?hide():show());},keydown=function(e){var handler=null,index,index2,pressedKeys=[],pressedModifiers={},currentKey=e.which,keyBindKeys,allModifiersPressed,pressed='p';keyState[currentKey]=pressed;for(index in keyState){if(keyState.hasOwnProperty(index)&&keyState[index]===pressed){pressedKeys.push(index);if(parseInt(index,10)!==currentKey){pressedModifiers[index]=true;}}}
for(index in options.keyBinds){if(options.keyBinds.hasOwnProperty(index)&&typeof(options.keyBinds[index])==='function'){keyBindKeys=index.split(' ');if(keyBindKeys.length===pressedKeys.length&&keyMap[currentKey]===keyBindKeys[keyBindKeys.length-1]){allModifiersPressed=true;for(index2=keyBindKeys.length-2;index2>=0;index2--){if(!(keyMap[keyBindKeys[index2]]in pressedModifiers)){allModifiersPressed=false;break;}}
if(allModifiersPressed){handler=options.keyBinds[index];break;}}}}
if(handler){handler.call(picker,widget);e.stopPropagation();e.preventDefault();}},keyup=function(e){keyState[e.which]='r';e.stopPropagation();e.preventDefault();},change=function(e){var val=$(e.target).val().trim(),parsedDate=val?parseInputDate(val):null;setValue(parsedDate);e.stopImmediatePropagation();return false;},attachDatePickerElementEvents=function(){input.on({'change':change,'blur':options.debug?'':hide,'keydown':keydown,'keyup':keyup,'focus':options.allowInputToggle?show:''});if(element.is('input')){input.on({'focus':show});}else if(component){component.on('click',toggle);component.on('mousedown',false);}},detachDatePickerElementEvents=function(){input.off({'change':change,'blur':blur,'keydown':keydown,'keyup':keyup,'focus':options.allowInputToggle?hide:''});if(element.is('input')){input.off({'focus':show});}else if(component){component.off('click',toggle);component.off('mousedown',false);}},indexGivenDates=function(givenDatesArray){var givenDatesIndexed={};$.each(givenDatesArray,function(){var dDate=parseInputDate(this);if(dDate.isValid()){givenDatesIndexed[dDate.format('YYYY-MM-DD')]=true;}});return(Object.keys(givenDatesIndexed).length)?givenDatesIndexed:false;},indexGivenHours=function(givenHoursArray){var givenHoursIndexed={};$.each(givenHoursArray,function(){givenHoursIndexed[this]=true;});return(Object.keys(givenHoursIndexed).length)?givenHoursIndexed:false;},initFormatting=function(){var format=options.format||'L LT';actualFormat=format.replace(/(\[[^\[]*\])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g,function(formatInput){var newinput=date.localeData().longDateFormat(formatInput)||formatInput;return newinput.replace(/(\[[^\[]*\])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g,function(formatInput2){return date.localeData().longDateFormat(formatInput2)||formatInput2;});});parseFormats=options.extraFormats?options.extraFormats.slice():[];if(parseFormats.indexOf(format)<0&&parseFormats.indexOf(actualFormat)<0){parseFormats.push(actualFormat);}
use24Hours=(actualFormat.toLowerCase().indexOf('a')<1&&actualFormat.replace(/\[.*?\]/g,'').indexOf('h')<1);if(isEnabled('y')){minViewModeNumber=2;}
if(isEnabled('M')){minViewModeNumber=1;}
if(isEnabled('d')){minViewModeNumber=0;}
currentViewMode=Math.max(minViewModeNumber,currentViewMode);if(!unset){setValue(date);}};picker.destroy=function(){hide();detachDatePickerElementEvents();element.removeData('DateTimePicker');element.removeData('date');};picker.toggle=toggle;picker.show=show;picker.hide=hide;picker.disable=function(){hide();if(component&&component.hasClass('btn')){component.addClass('disabled');}
input.prop('disabled',true);return picker;};picker.enable=function(){if(component&&component.hasClass('btn')){component.removeClass('disabled');}
input.prop('disabled',false);return picker;};picker.ignoreReadonly=function(ignoreReadonly){if(arguments.length===0){return options.ignoreReadonly;}
if(typeof ignoreReadonly!=='boolean'){throw new TypeError('ignoreReadonly () expects a boolean parameter');}
options.ignoreReadonly=ignoreReadonly;return picker;};picker.options=function(newOptions){if(arguments.length===0){return $.extend(true,{},options);}
if(!(newOptions instanceof Object)){throw new TypeError('options() options parameter should be an object');}
$.extend(true,options,newOptions);$.each(options,function(key,value){if(picker[key]!==undefined){picker[key](value);}else{throw new TypeError('option '+key+' is not recognized!');}});return picker;};picker.date=function(newDate){if(arguments.length===0){if(unset){return null;}
return date.clone();}
if(newDate!==null&&typeof newDate!=='string'&&!moment.isMoment(newDate)&&!(newDate instanceof Date)){throw new TypeError('date() parameter must be one of [null, string, moment or Date]');}
setValue(newDate===null?null:parseInputDate(newDate));return picker;};picker.format=function(newFormat){if(arguments.length===0){return options.format;}
if((typeof newFormat!=='string')&&((typeof newFormat!=='boolean')||(newFormat!==false))){throw new TypeError('format() expects a string or boolean:false parameter '+newFormat);}
options.format=newFormat;if(actualFormat){initFormatting();}
return picker;};picker.timeZone=function(newZone){if(arguments.length===0){return options.timeZone;}
if(typeof newZone!=='string'){throw new TypeError('newZone() expects a string parameter');}
options.timeZone=newZone;return picker;};picker.dayViewHeaderFormat=function(newFormat){if(arguments.length===0){return options.dayViewHeaderFormat;}
if(typeof newFormat!=='string'){throw new TypeError('dayViewHeaderFormat() expects a string parameter');}
options.dayViewHeaderFormat=newFormat;return picker;};picker.extraFormats=function(formats){if(arguments.length===0){return options.extraFormats;}
if(formats!==false&&!(formats instanceof Array)){throw new TypeError('extraFormats() expects an array or false parameter');}
options.extraFormats=formats;if(parseFormats){initFormatting();}
return picker;};picker.disabledDates=function(dates){if(arguments.length===0){return(options.disabledDates?$.extend({},options.disabledDates):options.disabledDates);}
if(!dates){options.disabledDates=false;update();return picker;}
if(!(dates instanceof Array)){throw new TypeError('disabledDates() expects an array parameter');}
options.disabledDates=indexGivenDates(dates);options.enabledDates=false;update();return picker;};picker.enabledDates=function(dates){if(arguments.length===0){return(options.enabledDates?$.extend({},options.enabledDates):options.enabledDates);}
if(!dates){options.enabledDates=false;update();return picker;}
if(!(dates instanceof Array)){throw new TypeError('enabledDates() expects an array parameter');}
options.enabledDates=indexGivenDates(dates);options.disabledDates=false;update();return picker;};picker.daysOfWeekDisabled=function(daysOfWeekDisabled){if(arguments.length===0){return options.daysOfWeekDisabled.splice(0);}
if((typeof daysOfWeekDisabled==='boolean')&&!daysOfWeekDisabled){options.daysOfWeekDisabled=false;update();return picker;}
if(!(daysOfWeekDisabled instanceof Array)){throw new TypeError('daysOfWeekDisabled() expects an array parameter');}
options.daysOfWeekDisabled=daysOfWeekDisabled.reduce(function(previousValue,currentValue){currentValue=parseInt(currentValue,10);if(currentValue>6||currentValue<0||isNaN(currentValue)){return previousValue;}
if(previousValue.indexOf(currentValue)===-1){previousValue.push(currentValue);}
return previousValue;},[]).sort();if(options.useCurrent&&!options.keepInvalid){var tries=0;while(!isValid(date,'d')){date.add(1,'d');if(tries===31){throw'Tried 31 times to find a valid date';}
tries++;}
setValue(date);}
update();return picker;};picker.maxDate=function(maxDate){if(arguments.length===0){return options.maxDate?options.maxDate.clone():options.maxDate;}
if((typeof maxDate==='boolean')&&maxDate===false){options.maxDate=false;update();return picker;}
if(typeof maxDate==='string'){if(maxDate==='now'||maxDate==='moment'){maxDate=getMoment();}}
var parsedDate=parseInputDate(maxDate);if(!parsedDate.isValid()){throw new TypeError('maxDate() Could not parse date parameter: '+maxDate);}
if(options.minDate&&parsedDate.isBefore(options.minDate)){throw new TypeError('maxDate() date parameter is before options.minDate: '+parsedDate.format(actualFormat));}
options.maxDate=parsedDate;if(options.useCurrent&&!options.keepInvalid&&date.isAfter(maxDate)){setValue(options.maxDate);}
if(viewDate.isAfter(parsedDate)){viewDate=parsedDate.clone().subtract(options.stepping,'m');}
update();return picker;};picker.minDate=function(minDate){if(arguments.length===0){return options.minDate?options.minDate.clone():options.minDate;}
if((typeof minDate==='boolean')&&minDate===false){options.minDate=false;update();return picker;}
if(typeof minDate==='string'){if(minDate==='now'||minDate==='moment'){minDate=getMoment();}}
var parsedDate=parseInputDate(minDate);if(!parsedDate.isValid()){throw new TypeError('minDate() Could not parse date parameter: '+minDate);}
if(options.maxDate&&parsedDate.isAfter(options.maxDate)){throw new TypeError('minDate() date parameter is after options.maxDate: '+parsedDate.format(actualFormat));}
options.minDate=parsedDate;if(options.useCurrent&&!options.keepInvalid&&date.isBefore(minDate)){setValue(options.minDate);}
if(viewDate.isBefore(parsedDate)){viewDate=parsedDate.clone().add(options.stepping,'m');}
update();return picker;};picker.defaultDate=function(defaultDate){if(arguments.length===0){return options.defaultDate?options.defaultDate.clone():options.defaultDate;}
if(!defaultDate){options.defaultDate=false;return picker;}
if(typeof defaultDate==='string'){if(defaultDate==='now'||defaultDate==='moment'){defaultDate=getMoment();}else{defaultDate=getMoment(defaultDate);}}
var parsedDate=parseInputDate(defaultDate);if(!parsedDate.isValid()){throw new TypeError('defaultDate() Could not parse date parameter: '+defaultDate);}
if(!isValid(parsedDate)){throw new TypeError('defaultDate() date passed is invalid according to component setup validations');}
options.defaultDate=parsedDate;if((options.defaultDate&&options.inline)||input.val().trim()===''){setValue(options.defaultDate);}
return picker;};picker.locale=function(locale){if(arguments.length===0){return options.locale;}
if(!moment.localeData(locale)){throw new TypeError('locale() locale '+locale+' is not loaded from moment locales!');}
options.locale=locale;date.locale(options.locale);viewDate.locale(options.locale);if(actualFormat){initFormatting();}
if(widget){hide();show();}
return picker;};picker.stepping=function(stepping){if(arguments.length===0){return options.stepping;}
stepping=parseInt(stepping,10);if(isNaN(stepping)||stepping<1){stepping=1;}
options.stepping=stepping;return picker;};picker.useCurrent=function(useCurrent){var useCurrentOptions=['year','month','day','hour','minute'];if(arguments.length===0){return options.useCurrent;}
if((typeof useCurrent!=='boolean')&&(typeof useCurrent!=='string')){throw new TypeError('useCurrent() expects a boolean or string parameter');}
if(typeof useCurrent==='string'&&useCurrentOptions.indexOf(useCurrent.toLowerCase())===-1){throw new TypeError('useCurrent() expects a string parameter of '+useCurrentOptions.join(', '));}
options.useCurrent=useCurrent;return picker;};picker.collapse=function(collapse){if(arguments.length===0){return options.collapse;}
if(typeof collapse!=='boolean'){throw new TypeError('collapse() expects a boolean parameter');}
if(options.collapse===collapse){return picker;}
options.collapse=collapse;if(widget){hide();show();}
return picker;};picker.icons=function(icons){if(arguments.length===0){return $.extend({},options.icons);}
if(!(icons instanceof Object)){throw new TypeError('icons() expects parameter to be an Object');}
$.extend(options.icons,icons);if(widget){hide();show();}
return picker;};picker.tooltips=function(tooltips){if(arguments.length===0){return $.extend({},options.tooltips);}
if(!(tooltips instanceof Object)){throw new TypeError('tooltips() expects parameter to be an Object');}
$.extend(options.tooltips,tooltips);if(widget){hide();show();}
return picker;};picker.useStrict=function(useStrict){if(arguments.length===0){return options.useStrict;}
if(typeof useStrict!=='boolean'){throw new TypeError('useStrict() expects a boolean parameter');}
options.useStrict=useStrict;return picker;};picker.sideBySide=function(sideBySide){if(arguments.length===0){return options.sideBySide;}
if(typeof sideBySide!=='boolean'){throw new TypeError('sideBySide() expects a boolean parameter');}
options.sideBySide=sideBySide;if(widget){hide();show();}
return picker;};picker.viewMode=function(viewMode){if(arguments.length===0){return options.viewMode;}
if(typeof viewMode!=='string'){throw new TypeError('viewMode() expects a string parameter');}
if(viewModes.indexOf(viewMode)===-1){throw new TypeError('viewMode() parameter must be one of ('+viewModes.join(', ')+') value');}
options.viewMode=viewMode;currentViewMode=Math.max(viewModes.indexOf(viewMode),minViewModeNumber);showMode();return picker;};picker.toolbarPlacement=function(toolbarPlacement){if(arguments.length===0){return options.toolbarPlacement;}
if(typeof toolbarPlacement!=='string'){throw new TypeError('toolbarPlacement() expects a string parameter');}
if(toolbarPlacements.indexOf(toolbarPlacement)===-1){throw new TypeError('toolbarPlacement() parameter must be one of ('+toolbarPlacements.join(', ')+') value');}
options.toolbarPlacement=toolbarPlacement;if(widget){hide();show();}
return picker;};picker.widgetPositioning=function(widgetPositioning){if(arguments.length===0){return $.extend({},options.widgetPositioning);}
if(({}).toString.call(widgetPositioning)!=='[object Object]'){throw new TypeError('widgetPositioning() expects an object variable');}
if(widgetPositioning.horizontal){if(typeof widgetPositioning.horizontal!=='string'){throw new TypeError('widgetPositioning() horizontal variable must be a string');}
widgetPositioning.horizontal=widgetPositioning.horizontal.toLowerCase();if(horizontalModes.indexOf(widgetPositioning.horizontal)===-1){throw new TypeError('widgetPositioning() expects horizontal parameter to be one of ('+horizontalModes.join(', ')+')');}
options.widgetPositioning.horizontal=widgetPositioning.horizontal;}
if(widgetPositioning.vertical){if(typeof widgetPositioning.vertical!=='string'){throw new TypeError('widgetPositioning() vertical variable must be a string');}
widgetPositioning.vertical=widgetPositioning.vertical.toLowerCase();if(verticalModes.indexOf(widgetPositioning.vertical)===-1){throw new TypeError('widgetPositioning() expects vertical parameter to be one of ('+verticalModes.join(', ')+')');}
options.widgetPositioning.vertical=widgetPositioning.vertical;}
update();return picker;};picker.calendarWeeks=function(calendarWeeks){if(arguments.length===0){return options.calendarWeeks;}
if(typeof calendarWeeks!=='boolean'){throw new TypeError('calendarWeeks() expects parameter to be a boolean value');}
options.calendarWeeks=calendarWeeks;update();return picker;};picker.showTodayButton=function(showTodayButton){if(arguments.length===0){return options.showTodayButton;}
if(typeof showTodayButton!=='boolean'){throw new TypeError('showTodayButton() expects a boolean parameter');}
options.showTodayButton=showTodayButton;if(widget){hide();show();}
return picker;};picker.showClear=function(showClear){if(arguments.length===0){return options.showClear;}
if(typeof showClear!=='boolean'){throw new TypeError('showClear() expects a boolean parameter');}
options.showClear=showClear;if(widget){hide();show();}
return picker;};picker.widgetParent=function(widgetParent){if(arguments.length===0){return options.widgetParent;}
if(typeof widgetParent==='string'){widgetParent=$(widgetParent);}
if(widgetParent!==null&&(typeof widgetParent!=='string'&&!(widgetParent instanceof $))){throw new TypeError('widgetParent() expects a string or a jQuery object parameter');}
options.widgetParent=widgetParent;if(widget){hide();show();}
return picker;};picker.keepOpen=function(keepOpen){if(arguments.length===0){return options.keepOpen;}
if(typeof keepOpen!=='boolean'){throw new TypeError('keepOpen() expects a boolean parameter');}
options.keepOpen=keepOpen;return picker;};picker.focusOnShow=function(focusOnShow){if(arguments.length===0){return options.focusOnShow;}
if(typeof focusOnShow!=='boolean'){throw new TypeError('focusOnShow() expects a boolean parameter');}
options.focusOnShow=focusOnShow;return picker;};picker.inline=function(inline){if(arguments.length===0){return options.inline;}
if(typeof inline!=='boolean'){throw new TypeError('inline() expects a boolean parameter');}
options.inline=inline;return picker;};picker.clear=function(){clear();return picker;};picker.keyBinds=function(keyBinds){if(arguments.length===0){return options.keyBinds;}
options.keyBinds=keyBinds;return picker;};picker.getMoment=function(d){return getMoment(d);};picker.debug=function(debug){if(typeof debug!=='boolean'){throw new TypeError('debug() expects a boolean parameter');}
options.debug=debug;return picker;};picker.allowInputToggle=function(allowInputToggle){if(arguments.length===0){return options.allowInputToggle;}
if(typeof allowInputToggle!=='boolean'){throw new TypeError('allowInputToggle() expects a boolean parameter');}
options.allowInputToggle=allowInputToggle;return picker;};picker.showClose=function(showClose){if(arguments.length===0){return options.showClose;}
if(typeof showClose!=='boolean'){throw new TypeError('showClose() expects a boolean parameter');}
options.showClose=showClose;return picker;};picker.keepInvalid=function(keepInvalid){if(arguments.length===0){return options.keepInvalid;}
if(typeof keepInvalid!=='boolean'){throw new TypeError('keepInvalid() expects a boolean parameter');}
options.keepInvalid=keepInvalid;return picker;};picker.datepickerInput=function(datepickerInput){if(arguments.length===0){return options.datepickerInput;}
if(typeof datepickerInput!=='string'){throw new TypeError('datepickerInput() expects a string parameter');}
options.datepickerInput=datepickerInput;return picker;};picker.parseInputDate=function(parseInputDate){if(arguments.length===0){return options.parseInputDate;}
if(typeof parseInputDate!=='function'){throw new TypeError('parseInputDate() sholud be as function');}
options.parseInputDate=parseInputDate;return picker;};picker.disabledTimeIntervals=function(disabledTimeIntervals){if(arguments.length===0){return(options.disabledTimeIntervals?$.extend({},options.disabledTimeIntervals):options.disabledTimeIntervals);}
if(!disabledTimeIntervals){options.disabledTimeIntervals=false;update();return picker;}
if(!(disabledTimeIntervals instanceof Array)){throw new TypeError('disabledTimeIntervals() expects an array parameter');}
options.disabledTimeIntervals=disabledTimeIntervals;update();return picker;};picker.disabledHours=function(hours){if(arguments.length===0){return(options.disabledHours?$.extend({},options.disabledHours):options.disabledHours);}
if(!hours){options.disabledHours=false;update();return picker;}
if(!(hours instanceof Array)){throw new TypeError('disabledHours() expects an array parameter');}
options.disabledHours=indexGivenHours(hours);options.enabledHours=false;if(options.useCurrent&&!options.keepInvalid){var tries=0;while(!isValid(date,'h')){date.add(1,'h');if(tries===24){throw'Tried 24 times to find a valid date';}
tries++;}
setValue(date);}
update();return picker;};picker.enabledHours=function(hours){if(arguments.length===0){return(options.enabledHours?$.extend({},options.enabledHours):options.enabledHours);}
if(!hours){options.enabledHours=false;update();return picker;}
if(!(hours instanceof Array)){throw new TypeError('enabledHours() expects an array parameter');}
options.enabledHours=indexGivenHours(hours);options.disabledHours=false;if(options.useCurrent&&!options.keepInvalid){var tries=0;while(!isValid(date,'h')){date.add(1,'h');if(tries===24){throw'Tried 24 times to find a valid date';}
tries++;}
setValue(date);}
update();return picker;};picker.viewDate=function(newDate){if(arguments.length===0){return viewDate.clone();}
if(!newDate){viewDate=date.clone();return picker;}
if(typeof newDate!=='string'&&!moment.isMoment(newDate)&&!(newDate instanceof Date)){throw new TypeError('viewDate() parameter must be one of [string, moment or Date]');}
viewDate=parseInputDate(newDate);viewUpdate();return picker;};if(element.is('input')){input=element;}else{input=element.find(options.datepickerInput);if(input.length===0){input=element.find('input');}else if(!input.is('input')){throw new Error('CSS class "'+options.datepickerInput+'" cannot be applied to non input element');}}
if(element.hasClass('input-group')){if(element.find('.datepickerbutton').length===0){component=element.find('.input-group-addon');}else{component=element.find('.datepickerbutton');}}
if(!options.inline&&!input.is('input')){throw new Error('Could not initialize DateTimePicker without an input element');}
date=getMoment();viewDate=date.clone();$.extend(true,options,dataToOptions());picker.options(options);initFormatting();attachDatePickerElementEvents();if(input.prop('disabled')){picker.disable();}
if(input.is('input')&&input.val().trim().length!==0){setValue(parseInputDate(input.val().trim()));}
else if(options.defaultDate&&input.attr('placeholder')===undefined){setValue(options.defaultDate);}
if(options.inline){show();}
return picker;};$.fn.datetimepicker=function(options){options=options||{};var args=Array.prototype.slice.call(arguments,1),isInstance=true,thisMethods=['destroy','hide','show','toggle'],returnValue;if(typeof options==='object'){return this.each(function(){var $this=$(this),_options;if(!$this.data('DateTimePicker')){_options=$.extend(true,{},$.fn.datetimepicker.defaults,options);$this.data('DateTimePicker',dateTimePicker($this,_options));}});}else if(typeof options==='string'){this.each(function(){var $this=$(this),instance=$this.data('DateTimePicker');if(!instance){throw new Error('bootstrap-datetimepicker("'+options+'") method was called on an element that is not using DateTimePicker');}
returnValue=instance[options].apply(instance,args);isInstance=returnValue===instance;});if(isInstance||$.inArray(options,thisMethods)>-1){return this;}
return returnValue;}
throw new TypeError('Invalid arguments for DateTimePicker: '+options);};$.fn.datetimepicker.defaults={timeZone:'',format:false,dayViewHeaderFormat:'MMMM YYYY',extraFormats:false,stepping:1,minDate:false,maxDate:false,useCurrent:true,collapse:true,locale:moment.locale(),defaultDate:false,disabledDates:false,enabledDates:false,icons:{time:'glyphicon glyphicon-time',date:'glyphicon glyphicon-calendar',up:'glyphicon glyphicon-chevron-up',down:'glyphicon glyphicon-chevron-down',previous:'glyphicon glyphicon-chevron-left',next:'glyphicon glyphicon-chevron-right',today:'glyphicon glyphicon-screenshot',clear:'glyphicon glyphicon-trash',close:'glyphicon glyphicon-remove'},tooltips:{today:'Go to today',clear:'Clear selection',close:'Close the picker',selectMonth:'Select Month',prevMonth:'Previous Month',nextMonth:'Next Month',selectYear:'Select Year',prevYear:'Previous Year',nextYear:'Next Year',selectDecade:'Select Decade',prevDecade:'Previous Decade',nextDecade:'Next Decade',prevCentury:'Previous Century',nextCentury:'Next Century',pickHour:'Pick Hour',incrementHour:'Increment Hour',decrementHour:'Decrement Hour',pickMinute:'Pick Minute',incrementMinute:'Increment Minute',decrementMinute:'Decrement Minute',pickSecond:'Pick Second',incrementSecond:'Increment Second',decrementSecond:'Decrement Second',togglePeriod:'Toggle Period',selectTime:'Select Time'},useStrict:false,sideBySide:false,daysOfWeekDisabled:false,calendarWeeks:false,viewMode:'days',toolbarPlacement:'default',showTodayButton:false,showClear:false,showClose:false,widgetPositioning:{horizontal:'auto',vertical:'auto'},widgetParent:null,ignoreReadonly:false,keepOpen:false,focusOnShow:true,inline:false,keepInvalid:false,datepickerInput:'.datepickerinput',keyBinds:{up:function(widget){if(!widget){return;}
var d=this.date()||this.getMoment();if(widget.find('.datepicker').is(':visible')){this.date(d.clone().subtract(7,'d'));}else{this.date(d.clone().add(this.stepping(),'m'));}},down:function(widget){if(!widget){this.show();return;}
var d=this.date()||this.getMoment();if(widget.find('.datepicker').is(':visible')){this.date(d.clone().add(7,'d'));}else{this.date(d.clone().subtract(this.stepping(),'m'));}},'control up':function(widget){if(!widget){return;}
var d=this.date()||this.getMoment();if(widget.find('.datepicker').is(':visible')){this.date(d.clone().subtract(1,'y'));}else{this.date(d.clone().add(1,'h'));}},'control down':function(widget){if(!widget){return;}
var d=this.date()||this.getMoment();if(widget.find('.datepicker').is(':visible')){this.date(d.clone().add(1,'y'));}else{this.date(d.clone().subtract(1,'h'));}},left:function(widget){if(!widget){return;}
var d=this.date()||this.getMoment();if(widget.find('.datepicker').is(':visible')){this.date(d.clone().subtract(1,'d'));}},right:function(widget){if(!widget){return;}
var d=this.date()||this.getMoment();if(widget.find('.datepicker').is(':visible')){this.date(d.clone().add(1,'d'));}},pageUp:function(widget){if(!widget){return;}
var d=this.date()||this.getMoment();if(widget.find('.datepicker').is(':visible')){this.date(d.clone().subtract(1,'M'));}},pageDown:function(widget){if(!widget){return;}
var d=this.date()||this.getMoment();if(widget.find('.datepicker').is(':visible')){this.date(d.clone().add(1,'M'));}},enter:function(){this.hide();},escape:function(){this.hide();},'control space':function(widget){if(!widget){return;}
if(widget.find('.timepicker').is(':visible')){widget.find('.btn[data-action="togglePeriod"]').click();}},t:function(){this.date(this.getMoment());},'delete':function(){this.clear();}},debug:false,allowInputToggle:false,disabledTimeIntervals:false,disabledHours:false,enabledHours:false,viewDate:false};return $.fn.datetimepicker;}));(function(){setInterval(update_system_info,1000);$('#btn_time_set').click(function(){$('#sys_time').val(moment().format('HH:mm:ss YYYY-MM-DD'));});$('#log_output').highlightWithinTextarea({highlight:[{highlight:/error/gi,className:'red'},{highlight:/warning/gi,className:'yellow'},{highlight:/info/gi,className:'blue'}]});$('#datetimepicker1').datetimepicker({format:'HH:mm:ss YYYY-MM-DD'});$("#tz_zone").select2({theme:"bootstrap"});})();function get_progress_values(input){var ret_values=[0,0,0];if(input>100){return ret_values;}else{ret_values[0]=input;}
if(input>50){ret_values[1]=ret_values[0]-50;ret_values[0]=50;if(ret_values[1]>25){ret_values[2]=ret_values[1]-25;ret_values[1]=25;}}
return ret_values;}
function update_system_info(){$.ajax({url:"/system/status",success:function(result){var mem=get_progress_values(result.memory_usage);$('#memory_info_header').html(result.memory_usage+'% of '+(result.memory_total/1000000000).toFixed(2)+'GB Used');$('#memory1').css({'width':mem[0]+'%'});$('#memory2').css({'width':mem[1]+'%'});$('#memory3').css({'width':mem[2]+'%'});var cpu=get_progress_values(result.cpu_load[0]);$('#cpu_info_header').html(result.cpu_load[0]+'%');$('#cpu1').css({'width':cpu[0]+'%'});$('#cpu2').css({'width':cpu[1]+'%'});$('#cpu3').css({'width':cpu[2]+'%'});var storage=get_progress_values(result.storage);$('#storage_info_header').html(result.storage+'% of 4GB Used');$('#storage1').css({'width':storage[0]+'%'});$('#storage2').css({'width':storage[1]+'%'});$('#storage3').css({'width':storage[2]+'%'});uptime=result.uptime.split(':');$('#uptime_info').html(uptime[0]+'h '+uptime[1]+'m '+uptime[2]+'s');$('#system_time_info').html(result.time);$.each(result.readers,function(index,value){if(value==='DISCONNECTED'){console.log('Disconnected');$('#reader'+index+'_header').html('<div class="led-red"></div>');$('#reader'+index+'_info').html(value);}else if(value==='CONNECTED'){console.log('Connected');$('#reader'+index+'_header').html('<div class="led-green"></div>');$('#reader'+index+'_info').html(value);}});$.each(result.sensors,function(index,value){if(value==='INACTIVE'){$('#door'+index+'_header').html('<i class="fa fa fa-sign-in fa-2x"></i>');$('#door'+index+'_info').html(value);}else if(value==='ACTIVE'){$('#door'+index+'_header').html('<i class="fa fa fa-sign-out fa-2x"></i>');$('#door'+index+'_info').html(value);}});},error:function(msg){console.log('Error in request');}});}
function get_versions(current_modislock_ver,avail_modislock_ver,current_monitor_ver,avail_monitor_ver){current_modislock_ver=current_modislock_ver.split('.');avail_modislock_ver=avail_modislock_ver.split('.');current_monitor_ver=current_monitor_ver.split('.');avail_monitor_ver=avail_monitor_ver.split('.');var modislock_upg=false;var monitor_upg=false;for(i=0;i<3;i++){if(parseInt(avail_modislock_ver[i])>parseInt(current_modislock_ver[i])){modislock_upg=true;break;}}
for(i=0;i<3;i++){if(parseInt(avail_monitor_ver[i])>parseInt(current_monitor_ver[i])){monitor_upg=true;break;}}
$('#btn_admin').prop('disabled',!modislock_upg);$('#btn_monitor').prop('disabled',!monitor_upg);}