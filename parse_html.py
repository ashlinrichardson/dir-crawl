'''20171117 basic HTML parser example from stackoverflow
This example extracts href tags'''
from HTMLParser import HTMLParser


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        # Only parse the 'anchor' tag.
        if tag == "a":
            # Check the list of defined attributes.
            for name, value in attrs:
                # If href is defined, print it.
                if name == "href":
                    print "href", value


def parse(f):
    parser = MyHTMLParser()
    parser.feed(f)
