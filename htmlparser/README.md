An HTML parser using AST

HTML page consists of tags, names, attributes, etc. During the build of the HTML document, it is necessary to visit the text again to seperate the script part as well as identify the start tag's attributes pairs. 

Comments can be identified as they follow this sequence:
<!-- -->
The name is always !-- and the end is --. Need to iterate thorugh the tokens till certain token is met.

==============

https://www.w3.org/TR/WD-html-lex/

 Markup Declarations

Each SGML document begins with a document type declaration. Comment declarations and marked section delcarations are other types of markup declarations.

The string <! followed by a name begins a markup declaration. The name is followed by parameters and a >. A [ in the parameters opens a declaration subset, which is a construct prohibited by this report.

The string <!-- begins a comment declaration. The -- begins a comment, which continues until the next occurrence of --. A comment declaration can contain zero or more comments. The string <!> is an empty comment declaration.

The string <![ begins a marked section declaration, which is prohibited by this report.

For example:

<!doctype foo>
<!DOCTYPE foo SYSTEM>
<!doctype bar system "abcdef">
<!doctype BaZ public "-//owner//DTD description//EN">
<!doctype BAZ Public "-//owner//DTD desc//EN" "sysid">
<!>
another way to escape < and &: <<!>xxx &<!>abc;
<!-- xyz -->
<!-- xyz -- --def-->
<!---- ---- ---->
<!------------>
<!doctype foo --my document type-- system "abc">

The following examples contain no markup. They illustrate that "<!" does not always signal markup.

<! doctype> <!,doctype> <!23>
<!- xxx -> <!-> <!-!>

The following are errors:

<!doctype xxx,yyy>
<!usemap map1>
<!-- comment-- xxx>
<!-- comment -- ->
<!----->

The following are errors, but they are not reported by this lexical analyzer.

<!doctype foo foo foo>
<!doctype foo 23 17>
<!junk decl>

The following are valid SGML constructs that are prohibited by this report:

<!doctype doc [ <!element doc - - ANY> ]>
<![ IGNORE [ lkjsdflkj sdflkj sdflkj  ]]>
<![ CDATA [ lskdjf lskdjf lksjdf ]]>

Tags

Tags are used to delimit elements. Most elements have a start-tag, some content, and end-tag. Empty elements have only a start-tag. For some elements, the start-tag and/or end-tag are optional. Empty elements and optional tags are structural constructs specified in the DTD, not lexical issues.

A start-tag begins with < followed by a name, and ends with >. The name refers to an element declaration in the DTD. An end-tag is similar, but begins with </.

For example:

<x> yyy </X>
<abc.DEF   > ggg </abc.def >
<abc123.-23>
<A>abc def <b>xxx</b>def</a>
<A>abc def <b>xxxdef</a>

The following examples contain no markup. They illustrate that a the < and </ strings do not always signal markup.

< x > <324 </234>
<==> < b>
<%%%> <---> <...> <--->

The following examples are errors:

<xyz!> <abc/>
</xxx/> <xyz&def> <abc_def>

These last few examples illustrate valid SGML constructs that are prohibited in the languages described by this report:

<> xyz </>
<xxx<yyy> </yyy</xxx>
<xxx/content/

Names

A name is a name-start characer -- a letter -- followed by any number of name characters -- letters, digits, periods, or hyphens. Entity names are case sensitive, but all other names are not.
Attributes

Start tags may contain attribute specifications. An attribute specification consists of a name, an "=" and a value specification. The name refers to an item in an ATTLIST declaration.

The value can be a name token or an attribute value literal. A name token is one or more name characters. An attribute value literal is a string delimited by double-quotes (") or a string delimited by single-quotes ('). Interpretation of attribute value literals is covered in the discussion of the lexical analyzer API.

If the ATTLIST declaration specifies an enumerated list of names, and the value specification is one of those names, the attribute name and "=" may be omitted.

For example:

<x attr="val">
<x ATTR ="val" val>
<y aTTr1= "val1">
<yy attr1='xyz' attr2="def" attr3='xy"z' attr4="abc'def">
<xx abc='abc&#34;def'>
<xx aBC="fred &amp; barney">
<z attr1 = val1 attr2 = 23 attr3 = 'abc'>
<xx val1 val2 attr3=.76meters>
<a href=foo.html> ..</a> <a href=foo-bar.html>..</a>

The following examples illustrate errors:

<x attr = abc$#@>
<y attr1,attr2>
<tt =xyz>
<z attr += 2>
<xx attr=50%>
<a href=http://foo/bar/>
<a href="http://foo/bar/> ... </a> ... <a href="xyz">...</a>
<xx "abc">
<xxx abc=>

Character References and Entity References

Characters in the document character set can be referred to by numeric character references. Entities declared in the DTD can be referred to by entity references.

An entity reference begins with "&" followed by a name, followed by an optional semicolon.

A numeric character reference begins with "&#" followed by a number followed by an optional semicolon. (The string "&#" followed by a name is a construct prohibited by this report.) A number is a sequence of digits.

The following examples illustrate character references and entity references:

&#38; &#200;
&amp; &ouml;
&#38 &#200,xxx
&amp &abc() &xy12/..\
To illustrate the X tag, write &lt;X&gt;

These examples contain no markup. They illustrate that "&" does not always signal markup.

a & b, a &# b
a &, b &. c
a &#-xx &100

These examples are errors:

&#2000000; &#20.7 &#20-35
&#23x;

The following are valid SGML, but prohibited by this report:

&#SPACE;
&#RE;

Processing Instructions

Processing instructions are a mechanism to capture platform-specific idioms. A processing instruction begins with <? and ends with >.

For example:

<?>
<?style tt = font courier>
<?page break>
<?experiment> ... <?/experiment> 

HTML is not a Context Free grammar. I should not use this method to parse html