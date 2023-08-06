from docutils import nodes
import traceback
from docutils.parsers.rst import Directive
from past.builtins import basestring
from sphinx.locale import _
from six.moves.urllib import parse as urlparse   # Retain Py2 compatibility for urlparse
import requests
from requests_file import FileAdapter
import json

class swaggerv2doc(nodes.Admonition, nodes.Element):
    pass

def visit_swaggerv2doc_node(self, node):
    self.visit_admonition(node)

def depart_swaggerv2doc_node(self, node):
    self.depart_admonition(node)

class SwaggerV2DocDirective(Directive):
    DEFAULT_GROUP = ''
    has_content = True
    def processSwaggerURL(self, url):
        parsed_url = urlparse.urlparse(url)
        if not parsed_url.scheme:
            env = self.state.document.settings.env
            relfn, absfn = env.relfn2path(url)
            env.note_dependency(relfn)
            with open(absfn) as fd:
                content = fd.read()
            return json.loads(content)
        else:
            s = requests.Session()
            s.mount('file://', FileAdapter())
            r = s.get(url)
            return r.json()

    def create_item(self, key, value):
        item = nodes.list_item()
        p = nodes.paragraph()
        p += nodes.strong('', key)
        p += nodes.Text(value)
        item += p
        return item

    def create_items(self, key, values):
        item = nodes.list_item()
        p = nodes.paragraph()
        bullet_list = nodes.bullet_list()
        for value in values:
            bullet_list += self.create_item('', value)
        p += nodes.strong('', key)
        item += p
        item += bullet_list
        return item

    def expand_values(self, list):
        expanded_values = ''
        for value in list:
            expanded_values += value + ' '
        return expanded_values

    def cell(self, contents):
        if isinstance(contents, basestring):
            contents = nodes.paragraph(text=contents)
        return nodes.entry('', contents)

    def row(self, cells):
        return nodes.row('', *[self.cell(c) for c in cells])

    def create_table(self, head, body, colspec=None):
        table = nodes.table()
        tgroup = nodes.tgroup()
        table.append(tgroup)
        if colspec is None:
            colspec = [1 for n in range(len(head))]
        for width in colspec:
            tgroup.append(nodes.colspec(colwidth=width))
        thead = nodes.thead()
        thead.append(self.row(head))
        tgroup.append(thead)
        tbody = nodes.tbody()
        tbody.extend([self.row(r) for r in body])
        tgroup.append(tbody)
        return table

    def make_responses(self, responses):
        entries = []
        paragraph = nodes.paragraph()
        paragraph += nodes.strong('', 'Responses' if len(responses) > 1 else 'Response')
        entries.append(paragraph)
        head = ['Name', 'Type', 'Example', 'Description']
        for response_name, response in responses.items():
            paragraph = nodes.paragraph()
            if len(responses) > 1:
                paragraph += nodes.emphasis(
                    '',
                    '%s - %s' % (response_name, response.get('description', ''))
                )
            entries.append(paragraph)
            body = []
            if isinstance(response.get('schema'), dict) and 'properties' in response.get('schema'):
                for property_name, property in response.get('schema').get('properties', {}).items():
                    row = []
                    row.append(nodes.strong('', property_name))
                    row.append(nodes.emphasis('', property.get('type', '')))
                    row.append(property.get('example', ''))
                    row.append(property.get('description', ''))
                    body.append(row)
                table = self.create_table(head, body)
                entries.append(table)
        if len(entries) < 3:
            return []
        return entries

    def make_body(self, parameters):
        entries = []
        head = ['Name', 'Type', 'Example', 'Description']
        body = []
        for param in parameters:
            if param.get('in', '') == 'body':
                if 'schema' in param and 'properties' in param['schema']:
                    for key, body_param in param['schema']['properties'].items():
                        row = []
                        row.append(nodes.strong('', key))
                        row.append(nodes.emphasis('', body_param.get('type', '')))
                        row.append(body_param.get('example', ''))
                        row.append(body_param.get('description', ''))
                        body.append(row)
                else:
                    row = []
                    row.append(nodes.strong('', param.get('name', '')))
                    row.append(nodes.emphasis('', param.get('type', '')))
                    row.append(body_param.get('example', ''))
                    row.append(param.get('description', ''))
                    body.append(row)
        if len(body) > 0:
            table = self.create_table(head, body)
            paragraph = nodes.paragraph()
            paragraph += nodes.strong('', 'Body')
            entries.append(paragraph)
            entries.append(table)
        return entries

    def make_query(self, parameters):
        entries = []
        head = ['Name', 'Type', 'Example', 'Description']
        body = []
        for param in parameters:
            if param.get('in', '') == 'query':
                row = []
                if 'schema' in param and 'type' in param['schema']:
                    row.append(nodes.strong('', param.get('name', '')))
                    row.append(nodes.emphasis('', param['schema'].get('type', '')))
                    row.append(param['schema'].get('example', ''))
                    row.append(param.get('description', ''))
                else:
                    row.append(nodes.strong('', param.get('name', '')))
                    row.append(nodes.emphasis('', param.get('type', '')))
                    row.append('')
                    row.append(param.get('description', ''))
                body.append(row)
        if len(body) > 0:
            table = self.create_table(head, body)
            paragraph = nodes.paragraph()
            paragraph += nodes.strong('', 'Query')
            entries.append(paragraph)
            entries.append(table)
        return entries

    def make_headers(self, parameters):
        entries = []
        head = ['Name', 'Type', 'Description']
        body = []
        for param in parameters:
            if param.get('in', '') == 'headers':
                row = []
                row.append(param.get('name', ''))
                row.append(nodes.emphasis('', param.get('type', '')))
                row.append(param.get('description', ''))
                body.append(row)
        if len(body) > 0:
            table = self.create_table(head, body)
            paragraph = nodes.paragraph()
            paragraph += nodes.strong('', 'Headers')
            entries.append(paragraph)
            entries.append(table)
        return entries

    def make_method(self, path, method_type, method):
        swagger_node = swaggerv2doc(path)
        swagger_node += nodes.title(path, method_type.upper() + ' ' + path)
        paragraph = nodes.paragraph()
        paragraph += nodes.Text(method.get('summary', '') or method.get('description', ''))
        bullet_list = nodes.bullet_list()
        method_sections = {'Description': 'description', 'Consumes': 'consumes', 'Produces': 'produces'}
        for title in method_sections:
            if title == 'Description' and not len(method.get('summary', '')):
                continue;
            value_name = method_sections[title]
            value = method.get(value_name)
            if value is not None:
                if (isinstance(value, str)):
                    bullet_list += self.create_item(title + ': \n', value)
                else:
                    bullet_list += self.create_items(title + ': \n', value)
        paragraph += bullet_list
        swagger_node += paragraph
        parameters = method.get('parameters')
        if parameters is not None:
            swagger_node += self.make_headers(parameters)
            swagger_node += self.make_query(parameters)
            swagger_node += self.make_body(parameters)
        responses = method.get('responses')
        if responses is not None:
            swagger_node += self.make_responses(responses)
        return [swagger_node]

    def group_tags(self, api_desc):
        groups = {}
        if 'tags' in api_desc:
            for tag in api_desc['tags']:
                groups[tag['name']] = []
        if len(groups) == 0:
            groups[SwaggerV2DocDirective.DEFAULT_GROUP] = []
        for path, methods in api_desc['paths'].items():
            for method_type, method in methods.items():
                if SwaggerV2DocDirective.DEFAULT_GROUP in groups:
                    groups[SwaggerV2DocDirective.DEFAULT_GROUP].append((path, method_type, method))
                else:
                    for tag in method['tags']:
                        groups.setdefault(tag, []).append((path, method_type, method))
        return groups

    def create_section(self, title):
        section = nodes.section(ids=[title])
        section += nodes.title(title, title)
        return section

    def check_tags(self, selected_tags, tags, api_url):
        invalid_tags = list(set(selected_tags) - set(tags))
        if len(invalid_tags) > 0:
            msg = self.reporter.error("Error. Tag '%s' not found in Swagger URL %s." % (invalid_tags[0], api_url))
            return [msg]

    def run(self):
        self.reporter = self.state.document.reporter
        api_url = self.content[0]
        if len(self.content) > 1:
            selected_tags = self.content[1:]
        else:
            selected_tags = []
        try:
            api_desc = self.processSwaggerURL(api_url)
            groups = self.group_tags(api_desc)
            self.check_tags(selected_tags, groups.keys(), api_url)
            entries = []
            for tag_name, methods in groups.items():
                if tag_name in selected_tags or len(selected_tags) == 0:
                    section = self.create_section(tag_name)
                    for path, method_type, method in methods:
                        section += self.make_method(path, method_type, method)
                    entries.append(section)
            return entries
        except Exception as e:
            error_message = 'Unable to process URL: %s' % api_url
            print(error_message)
            traceback.print_exc()
            error = nodes.error('')
            para_error = nodes.paragraph()
            para_error += nodes.Text(
                error_message + '. Please check that the URL is a valid Swagger api-docs URL and it is accesible'
            )
            para_error_detailed = nodes.paragraph()
            para_error_detailed = nodes.strong('Processing error. See console output for a more detailed error')
            error += para_error
            error += para_error_detailed
            return [error]
