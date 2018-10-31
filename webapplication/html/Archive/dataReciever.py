import cgi , cgitb


form = cgi.FeildStorage()

if form.getValue('coordinatesData'):
    coordinates = form.getValue('coordinatesData')
else:
    coordinates = 'Not fetched'

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>";
print "<title>Text Area - Fifth CGI Program</title>"
print "</head>"
print "<body>"
print "<h2> Entered Text Content is %s</h2>" % text_content
print "</body>"