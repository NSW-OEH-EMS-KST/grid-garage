<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                version="1.0">

<xsl:output method="html"/>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!-- MdDlgHelp.xsl                                          -->
<!--                                                        -->    
<!-- Style sheet used to generate the HTML file containing  --> 
<!-- the function/variable help information.                -->
<!--                                                        -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->


<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                       Variables                        -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->

<xsl:variable name="pre_path" select="//MdElementDialogInfo/HelpPath/text()"/>
<xsl:variable name="path" select="translate($pre_path, '\', '/')"/>

<xsl:variable name="Font">arial,verdana</xsl:variable>
<xsl:variable name="Margin">0em 0em 0em 0em</xsl:variable>
<xsl:variable name="BackgroundColor">White</xsl:variable>
<xsl:variable name="SmallFont">verdana,arial</xsl:variable>
<xsl:variable name="SmallSize">7pt</xsl:variable>
<xsl:variable name="SmallColor">Black</xsl:variable>
<xsl:variable name="SmallWeight">Normal</xsl:variable>
<xsl:variable name="SmallStyle">Normal</xsl:variable>
<xsl:variable name="ParaFont">arial,verdana</xsl:variable>
<xsl:variable name="ParaSize">10pt</xsl:variable>
<xsl:variable name="ParaColor">Black</xsl:variable>
<xsl:variable name="ParaWeight">Normal</xsl:variable>
<xsl:variable name="ParaStyle">Normal</xsl:variable>
<xsl:variable name="ULFont">arial,verdana</xsl:variable>
<xsl:variable name="ULSize">10pt</xsl:variable>
<xsl:variable name="ULColor">Black</xsl:variable>
<xsl:variable name="ULWeight">Normal</xsl:variable>
<xsl:variable name="ULStyle">Normal</xsl:variable>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                 <ElementHelp> Template                 -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="ElementHelp">
  <p><xsl:apply-templates select="text()" /></p>
  <xsl:apply-templates select="*" />
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                     Text Template                      -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="text()">
	<xsl:choose>
		<!-- Handle escaped HTML -->
		<xsl:when test="(contains(.,'&lt;/')) or (contains(.,'/&gt;'))">
			<xsl:value-of select="." disable-output-escaping="yes" />
		</xsl:when>
		<!-- Handle all other text -->
		<xsl:otherwise>
			<xsl:value-of select="." />
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                    <para> Template                     -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="para">
	<p>
		<xsl:apply-templates select="text() | *"/>
	</p>
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--               <bullet_item> Template                   -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="bulletList">
	<ul>
		<xsl:apply-templates select="bullet_item"/>
	</ul>
</xsl:template>

<xsl:template match="bullet_item">
	<li>
		<xsl:apply-templates select="*|text()"/>
	</li>
</xsl:template>


<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                  <indent> Template                     -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="indent">
	<dl>
		<dt/>
		<dd>
			<xsl:apply-templates select="*" />			
		</dd>
	</dl>
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                    <link> Template                     -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="link">
	<a TARGET="viewer">
		<xsl:attribute name="href">
			<xsl:choose>
				<xsl:when test="contains(@src, 'ARCTOOLBOXHELP')">
						<xsl:call-template name="ToolPath">
							<xsl:with-param name="fullpath" select="@src"/>
						</xsl:call-template> 
				</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="@src"/>
					</xsl:otherwise>						
				</xsl:choose>
		</xsl:attribute>
		<xsl:value-of select="." />
	</a>		
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                   <illust> Template                    -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="illust">
<br/>
	<img>
		<xsl:attribute name="src">
			<xsl:choose>
				<xsl:when test="contains(@src, 'ARCTOOLBOXHELP')">
						<xsl:call-template name="ToolPath">
							<xsl:with-param name="fullpath" select="@src"/>
						</xsl:call-template> 
				</xsl:when>
				<xsl:otherwise>
						<xsl:value-of select="@src"/>
				</xsl:otherwise>						
			</xsl:choose>
		</xsl:attribute>
		
		<xsl:attribute name="alt">
			<xsl:value-of select="@alt"/>
		</xsl:attribute>
	</img>
	<p/>
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                    <code> Template                     -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="code">
	<xsl:call-template name="codeMacro"/>
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                 <codeMacro> Template                   -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template name ="codeMacro">
	<pre>
		<xsl:apply-templates select="*|text()"/>
	</pre>
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                 <subSection> Template                  -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="subSection">
  <xsl:if test="*">
	  <p>
		  <h2>
			  <xsl:call-template name="ImageAndScript"/>
				  <xsl:text> </xsl:text><xsl:value-of select="@title"/>
		  </h2>	
	  </p>
	  <div>
		  <xsl:attribute name="Class">expand</xsl:attribute>
		  <xsl:attribute name="id"><xsl:value-of select="generate-id(.)"/></xsl:attribute>
		  <xsl:attribute name="style">display:None</xsl:attribute>
		  <xsl:apply-templates select="*"/>
	  </div>
  </xsl:if>
</xsl:template>	

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                <ImageAndScript> Template               -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template name="ImageAndScript">
  <a>
	  <xsl:variable name="NodeID" select="generate-id(.)"/>
		  <xsl:attribute name="href">#<xsl:value-of select="$NodeID"/></xsl:attribute>
		  <xsl:attribute name="onClick">expandIt('<xsl:value-of select="$NodeID"/>','<xsl:choose>
			  <xsl:when test="$path !=''">
				  <xsl:value-of select="concat($path, '/')"></xsl:value-of>	
			  </xsl:when>
			  <xsl:otherwise>
				  <xsl:value-of select="$path"></xsl:value-of>	
			  </xsl:otherwise>
		  </xsl:choose><xsl:text>','small_arrow_up.gif')</xsl:text>
		  </xsl:attribute>
		  <img width="11" height="11" alt="expand/collapse item" border="0" name="imEx" id="toolbox">
			  <xsl:attribute name="src">
					  <xsl:value-of select="$path"/>
						  <xsl:if test="$path !=''">
							  <xsl:text>/</xsl:text>
						  </xsl:if>
				  <xsl:text>small_arrow_up.gif</xsl:text>
			  </xsl:attribute>
		  </img>
  </a>
</xsl:template>	

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                   <ToolPath> Template                  -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template name="ToolPath">
	<xsl:param name="fullpath"/>
		<xsl:variable name="afterArcToolBoxHelp">
      <xsl:variable name="tempPath" select="substring-after($fullpath, '/')"/>
      <xsl:choose>
	      <xsl:when test="$tempPath !=''">
          <xsl:value-of select="$tempPath"/>
			  </xsl:when>
        <xsl:otherwise>
				  <xsl:value-of select="substring-after($fullpath, '\')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

		<xsl:variable name="srcPath">	
			<xsl:value-of select="$path"/>
			<xsl:if test="$path !=''">
				<xsl:text>/</xsl:text>
			</xsl:if>
			<xsl:value-of select="$afterArcToolBoxHelp"/>
		</xsl:variable>
		<xsl:value-of select="$srcPath"></xsl:value-of>
</xsl:template>		

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--              MdElementDialogInfo Template              -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="MdElementDialogInfo">
<HTML>
  <xsl:attribute name="DIR">
    <xsl:value-of select="Direction" />
  </xsl:attribute>
<xsl:text xml:space="preserve">&#x0D;&#x0A;</xsl:text>
<xsl:comment>&#x20;saved from url=(005)local&#x20;</xsl:comment><xsl:text xml:space="preserve">&#x0D;&#x0A;</xsl:text>
<HEAD>
<TITLE>Help</TITLE>

<STYLE TYPE="text/css">

BODY {    font-family:      <xsl:value-of select="$Font"/>; 
          margin:           <xsl:value-of select="$Margin"/>; 
          background-color: <xsl:value-of select="$BackgroundColor"/>; }

.small {  font-family:      <xsl:value-of select="$SmallFont"/>; 
          font-size:        <xsl:value-of select="$SmallSize"/>; 
          color:            <xsl:value-of select="$SmallColor"/>; 
          font-weight:      <xsl:value-of select="$SmallWeight"/>; 
          font-style:       <xsl:value-of select="$SmallStyle"/>; }  

P {       font-family:      <xsl:value-of select="$ParaFont"/>; 
          font-size:        <xsl:value-of select="$ParaSize"/>; 
          color:            <xsl:value-of select="$ParaColor"/>; 
          font-weight:      <xsl:value-of select="$ParaWeight"/>; 
          font-style:       <xsl:value-of select="$ParaStyle"/>; }

UL {      font-family:      <xsl:value-of select="$ULFont"/>; 
          font-size:        <xsl:value-of select="$ULSize"/>; 
          color:            <xsl:value-of select="$ULColor"/>; 
          font-weight:      <xsl:value-of select="$ULWeight"/>; 
          font-style:       <xsl:value-of select="$ULStyle"/>; }

</STYLE><xsl:text>&#10;</xsl:text>

<xsl:comment> ================ Scripts ================ </xsl:comment>
<xsl:text>&#10;</xsl:text>

<xsl:text>&#10;</xsl:text>

<SCRIPT language="JavaScript"><xsl:text>&#10;</xsl:text>
<xsl:comment>

<![CDATA[
function ShowArcGISHelp()
{
  window.external.ShowHelp();
}
var message="Function Disabled!";

function clickIE() {
	if (document.all) {
		//alert(message);
		return false;
	}
}
function clickNS(e) {
	if (document.layers||(document.getElementById&&!document.all)) {
		if (e.which==2||e.which==3) {
			//alert(message);
			return false;
		}
	}
}
if (document.layers) {
	document.captureEvents(Event.MOUSEDOWN);
	document.onmousedown=clickNS;
} else {
	document.onmouseup=clickNS;
	document.oncontextmenu=clickIE;
}

document.oncontextmenu=new Function("return false")
document.onmouseover = doOver;
document.onmouseout  = doOut;
document.onmousedown = doDown;
document.onmouseup   = doUp;

function doOver() {
	var toEl = getReal(window.event.toElement, "className", "coolButton");
	var fromEl = getReal(window.event.fromElement, "className", "coolButton");
	if (toEl == fromEl) return;
	var el = toEl;
	
	var cDisabled = el.cDisabled;
	cDisabled = (cDisabled != null); // If CDISABLED atribute is present
	
	if (el.className == "coolButton")
		el.onselectstart = new Function("return false");
	
	if ((el.className == "coolButton") && !cDisabled) {
		makeRaised(el);
		makeGray(el,false);
	}
}

function doOut() {
	var toEl = getReal(window.event.toElement, "className", "coolButton");
	var fromEl = getReal(window.event.fromElement, "className", "coolButton");
	if (toEl == fromEl) return;
	var el = fromEl;

	var cDisabled = el.cDisabled;
	cDisabled = (cDisabled != null); // If CDISABLED atribute is present

	var cToggle = el.cToggle;
	toggle_disabled = (cToggle != null); // If CTOGGLE atribute is present

	if (cToggle && el.value) {
		makePressed(el);
		makeGray(el,true);
	}
	else if ((el.className == "coolButton") && !cDisabled) {
		makeFlat(el);
		makeGray(el,true);
	}

}

function doDown() {
	el = getReal(window.event.srcElement, "className", "coolButton");
	
	var cDisabled = el.cDisabled;
	cDisabled = (cDisabled != null); // If CDISABLED atribute is present
	
	if ((el.className == "coolButton") && !cDisabled) {
		makePressed(el)
	}
}

function doUp() {
	el = getReal(window.event.srcElement, "className", "coolButton");
	
	var cDisabled = el.cDisabled;
	cDisabled = (cDisabled != null); // If CDISABLED atribute is present
	
	if ((el.className == "coolButton") && !cDisabled) {
		makeRaised(el);
	}
}

function getReal(el, type, value) {
	temp = el;
	while ((temp != null) && (temp.tagName != "BODY")) {
		if (eval("temp." + type) == value) {
			el = temp;
			return el;
		}
		temp = temp.parentElement;
	}
	return el;
}

function findChildren(el, type, value) {
	var children = el.children;
	var tmp = new Array();
	var j=0;
	
	for (var i=0; i<children.length; i++) {
		if (eval("children[i]." + type + "==\"" + value + "\"")) {
			tmp[tmp.length] = children[i];
		}
		tmp = tmp.concat(findChildren(children[i], type, value));
	}
	
	return tmp;
}

function disable(el) {

	if (document.readyState != "complete") {
		window.setTimeout("disable(" + el.id + ")", 100);	// If document not finished rendered try later.
		return;
	}
	
	var cDisabled = el.cDisabled;
	
	cDisabled = (cDisabled != null); // If CDISABLED atribute is present

	if (!cDisabled) {
		el.cDisabled = true;
		
		el.innerHTML = '<span style="background: buttonshadow; width: 100%; height: 100%; text-align: center;">' +
						'<span style="filter:Mask(Color=buttonface) DropShadow(Color=buttonhighlight, OffX=1, OffY=1, Positive=0); height: 100%; width: 100%%; text-align: center;">' +
						el.innerHTML +
						'</span>' +
						'</span>';

		if (el.onclick != null) {
			el.cDisabled_onclick = el.onclick;
			el.onclick = null;
		}
	}
}

function enable(el) {
	var cDisabled = el.cDisabled;
	
	cDisabled = (cDisabled != null); // If CDISABLED atribute is present
	
	if (cDisabled) {
		el.cDisabled = null;
		el.innerHTML = el.children[0].children[0].innerHTML;

		if (el.cDisabled_onclick != null) {
			el.onclick = el.cDisabled_onclick;
			el.cDisabled_onclick = null;
		}
	}
}

function addToggle(el) {
	var cDisabled = el.cDisabled;
	
	cDisabled = (cDisabled != null); // If CDISABLED atribute is present
	
	var cToggle = el.cToggle;
	
	cToggle = (cToggle != null); // If CTOGGLE atribute is present

	if (!cToggle && !cDisabled) {
		el.cToggle = true;
		
		if (el.value == null)
			el.value = 0;		// Start as not pressed down
		
		if (el.onclick != null)
			el.cToggle_onclick = el.onclick;	// Backup the onclick
		else 
			el.cToggle_onclick = "";

		el.onclick = new Function("toggle(" + el.id +"); " + el.id + ".cToggle_onclick();");
	}
}

function removeToggle(el) {
	var cDisabled = el.cDisabled;
	
	cDisabled = (cDisabled != null); // If CDISABLED atribute is present
	
	var cToggle = el.cToggle;
	
	cToggle = (cToggle != null); // If CTOGGLE atribute is present
	
	if (cToggle && !cDisabled) {
		el.cToggle = null;

		if (el.value) {
			toggle(el);
		}

		makeFlat(el);
		
		if (el.cToggle_onclick != null) {
			el.onclick = el.cToggle_onclick;
			el.cToggle_onclick = null;
		}
	}
}

function toggle(el) {
	el.value = !el.value;
	
	if (el.value)
		el.style.background = "URL(/images/tileback.gif)";
	else
		el.style.backgroundImage = "";

//	doOut(el);	
}


function makeFlat(el) {
	with (el.style) {
		background = "";
		border = "1px solid buttonface";
		padding      = "1px";
	}
}

function makeRaised(el) {
	with (el.style) {
		borderLeft   = "1px solid buttonhighlight";
		borderRight  = "1px solid buttonshadow";
		borderTop    = "1px solid buttonhighlight";
		borderBottom = "1px solid buttonshadow";
		padding      = "1px";
	}
}

function makePressed(el) {
	with (el.style) {
		borderLeft   = "1px solid buttonshadow";
		borderRight  = "1px solid buttonhighlight";
		borderTop    = "1px solid buttonshadow";
		borderBottom = "1px solid buttonhighlight";
		paddingTop    = "2px";
		paddingLeft   = "2px";
		paddingBottom = "0px";
		paddingRight  = "0px";
	}
}

function makeGray(el,b) {
	var filtval;
	
	if (b)
		filtval = "gray()";
	else
		filtval = "";

	var imgs = findChildren(el, "tagName", "IMG");
		
	for (var i=0; i<imgs.length; i++) {
		imgs[i].style.filter = filtval;
	}

}
	

document.write("<style>");
document.write(".coolBar	{background: buttonface;border-top: 1px solid buttonhighlight;	border-left: 1px solid buttonhighlight;	border-bottom: 1px solid buttonshadow; border-right: 1px solid buttonshadow; padding: 1px; font: menu;}");
document.write(".coolButton {border: 1px solid buttonface; padding: 1px; text-align: center; cursor: default;}");
document.write(".coolButton IMG	{filter: gray();}");
document.write("</style>");

function ShowHelpTopic(topic)
{
  document.getElementById("Intro").style.display = "none";
    
]]>
<xsl:for-each select="Properties/PropertyGroup"><xsl:for-each select="Property">  document.getElementById(&quot;<xsl:value-of select="PropertyName"/>Topic&quot;).style.display = "none";
</xsl:for-each></xsl:for-each><![CDATA[

  if (topic== '')
    topic = 'Intro';

  document.getElementById(topic).style.display = "block";
}

]]>
</xsl:comment><xsl:text>&#10;</xsl:text>
</SCRIPT><xsl:text>&#10;</xsl:text>

</HEAD><xsl:text>&#10;</xsl:text>

<BODY><xsl:text>&#10;</xsl:text>
<xsl:text>&#10;</xsl:text>

<xsl:comment>View Documentation...</xsl:comment><xsl:text>&#10;</xsl:text>

<xsl:text>&#10;</xsl:text>
<xsl:comment>General Description...</xsl:comment><xsl:text>&#10;</xsl:text>
<xsl:text>&#10;</xsl:text>

<DIV STYLE="margin:0.5em 0.5em 0.5em 1.0em;" ID="Intro" style="display:block;">
<B><xsl:value-of select="Title"/></B>
<xsl:apply-templates select="ElementHelp" />
</DIV><xsl:text>&#10;</xsl:text>

<xsl:text>&#10;</xsl:text>
<xsl:comment>Property Descriptions...</xsl:comment><xsl:text>&#10;</xsl:text>
<xsl:text>&#10;</xsl:text>

<xsl:for-each select="Properties/PropertyGroup">
  <xsl:for-each select="Property">
    <DIV STYLE="margin:0.5em 0.5em 0.5em 1.0em;" ID="{PropertyName}Topic" style="display:none;">
      <B><xsl:value-of select="PropertyLabel"/></B>
			<xsl:apply-templates select="PropertyHelp"/>
    </DIV><xsl:text>&#10;</xsl:text>
  </xsl:for-each>
</xsl:for-each>

<xsl:text>&#10;</xsl:text>
</BODY>
</HTML>
</xsl:template>

<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<!--                   Root Template                        -->
<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
<xsl:template match="/">
  <xsl:apply-templates />
</xsl:template>

</xsl:stylesheet>


