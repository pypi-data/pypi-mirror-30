from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, Namespace, Literal
from pyldapi import PYLDAPI
import _config as conf


class RegisterRenderer(Renderer):
    """
    Version 1.0
    """
    def __init__(self, request, contained_item_class_uri, contained_item_instance_base_uri, description=None):
        Renderer.__init__(self)

        self.request = request
        self.base_uri = contained_item_instance_base_uri
        self.uri = contained_item_class_uri
        self.register = []
        self.g = None
        self.description = description
        self.paging_params(self.request)

        self.load_data(self.page, self.per_page)

    def paging_params(self, request):
        # pagination
        self.page = int(request.args.get('page')) if request.args.get('page') is not None else 1
        self.per_page = int(request.args.get('per_page')) if request.args.get('per_page') is not None \
            else conf.PAGE_SIZE_DEFAULT

        if self.per_page > conf.PAGE_SIZE_MAX:
            return Response(
                'You must enter either no value for per_page or an integer <= {}.'.format(conf.PAGE_SIZE_MAX),
                status=400,
                mimetype='text/plain'
            )

        links = list()
        links.append('<http://www.w3.org/ns/ldp#Resource>; rel="type"')
        # signalling that this is, in fact, a resource described in pages
        links.append('<http://www.w3.org/ns/ldp#Page>; rel="type"')
        links.append('<{}?per_page={}>; rel="first"'.format(request.base_url, self.per_page))

        # if this isn't the first page, add a link to "prev"
        if self.page != 1:
            links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                request.base_url,
                self.per_page,
                (self.page - 1)
            ))

        # if this isn't the first page, add a link to "prev"
        if self.page != 1:
            self.prev_page = self.page - 1
            links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                request.base_url,
                self.per_page,
                self.prev_page
            ))
        else:
            self.prev_page = None

        # add a link to "next" and "last"
        try:
            r = requests.get(conf.XML_API_URL_SITES_TOTAL_COUNT)
            no_of_samples = int(r.content.decode('utf-8').split('<RECORD_COUNT>')[1].split('</RECORD_COUNT>')[0])
            self.last_page = int(round(no_of_samples / self.per_page, 0)) + 1  # same as math.ceil()

            # if we've gotten the last page value successfully, we can choke if someone enters a larger value
            if self.page > self.last_page:
                return Response(
                    'You must enter either no value for page or an integer <= {} which is the last page number.'
                    .format(self.last_page),
                    status=400,
                    mimetype='text/plain'
                )

            # add a link to "next"
            if self.page != self.last_page:
                self.next_page = self.page + 1
                links.append('<{}?per_page={}&page={}>; rel="next"'
                             .format(request.base_url, self.per_page, (self.page + 1)))
            else:
                self.next_page = None

            # add a link to "last"
            links.append('<{}?per_page={}&page={}>; rel="last"'
                            .format(request.base_url, self.per_page, self.last_page))
        except:
            # if there's some error in getting the no of samples, add the "next" link but not the "last" link
            self.next_page = self.page + 1
            links.append('<{}?per_page={}&page={}>; rel="next"'
                         .format(request.base_url, self.per_page, (self.page + 1)))
            self.last_page = None

        self.headers = {
            'Link': ', '.join(links)
        }

    def load_data(self, page, per_page):
        # this a stub that you need to replace with real data loading
        self.register = [
            'http://localhost:5000/widget/1',
            'http://localhost:5000/widget/2'
        ]

    @staticmethod
    def views_formats(description=None):
        return {
            'default': 'reg',
            'alternates': {
                'mimetypes':
                    ['text/html', 'text/turtle', 'application/rdf+xml', 'application/rdf+json', 'application/json'],
                'default_mimetype': 'text/html',
                'namespace': 'http://www.w3.org/ns/ldp#Alternates',
                'description': 'The view listing all other views of this class of object'
            },
            'reg': {
                'mimetypes': ['text/html', 'text/turtle', 'application/rdf+xml', 'application/rdf+json'],
                'default_mimetype': 'text/html',
                'namespace': 'http://purl.org/linked-data/registry#',
                'description':
                    'The Registry Ontology. Core ontology for linked data registry services. Based on ISO19135 but '
                    'heavily modified to suit Linked Data representations and applications',
            },
            'description':
                description
        }

    def render(self, view, mimetype):
        if view == 'reg':
            # is an RDF format requested?
            if mimetype in PYLDAPI.get_rdf_mimetypes_list():
                # it is an RDF format so make the graph for serialization
                self._make_reg_graph(view)
                rdflib_format = PYLDAPI.get_rdf_parser_for_mimetype(mimetype)
                return Response(
                    self.g.serialize(format=rdflib_format),
                    status=200,
                    mimetype=mimetype,
                    headers=self.headers
                )
            elif mimetype == 'text/html':
                return Response(
                    render_template(
                        'page_register.html',
                        base_uri=self.base_uri,
                        class_name=self.uri,
                        register=self.register,
                        page=self.page,
                        per_page=self.per_page,
                        prev_page=self.prev_page,
                        next_page=self.next_page,
                        last_page=self.last_page
                    ),
                    mimetype='text/html',
                    headers=self.headers
                )
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def _make_reg_graph(self, model_view):
        self.g = Graph()

        if model_view == 'reg':  # reg is default
            # make the static part of the graph
            REG = Namespace('http://purl.org/linked-data/registry#')
            self.g.bind('reg', REG)

            LDP = Namespace('http://www.w3.org/ns/ldp#')
            self.g.bind('ldp', LDP)

            XHV = Namespace('https://www.w3.org/1999/xhtml/vocab#')
            self.g.bind('xhv', XHV)

            register_uri = URIRef(self.request.base_url)
            self.g.add((register_uri, RDF.type, REG.Register))
            self.g.add((register_uri, RDFS.label, Literal('Sites Register', datatype=XSD.string)))

            page_uri_str = self.request.base_url
            if self.per_page is not None:
                page_uri_str += '?per_page=' + str(self.per_page)
            else:
                page_uri_str += '?per_page=100'
            page_uri_str_no_page_no = page_uri_str + '&page='
            if self.page is not None:
                page_uri_str += '&page=' + str(self.page)
            else:
                page_uri_str += '&page=1'
            page_uri = URIRef(page_uri_str)

            # pagination
            # this page
            self.g.add((page_uri, RDF.type, LDP.Page))
            self.g.add((page_uri, LDP.pageOf, register_uri))

            # links to other pages
            self.g.add((page_uri, XHV.first, URIRef(page_uri_str_no_page_no + '1')))
            self.g.add((page_uri, XHV.last, URIRef(page_uri_str_no_page_no + str(self.last_page))))

            if self.page != 1:
                self.g.add((page_uri, XHV.prev, URIRef(page_uri_str_no_page_no + str(self.page - 1))))

            if self.page != self.last_page:
                self.g.add((page_uri, XHV.next, URIRef(page_uri_str_no_page_no + str(self.page + 1))))

            # add all the items
            for item in self.register:
                item_uri = URIRef(self.request.base_url + item)
                self.g.add((item_uri, RDF.type, URIRef(self.uri)))
                self.g.add((item_uri, RDFS.label, Literal('Site:' + item, datatype=XSD.string)))
                self.g.add((item_uri, REG.register, page_uri))
