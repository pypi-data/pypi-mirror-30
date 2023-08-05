# -*- coding: utf-8 -*-
## Filename    : chart_xml.py
## Author(s)   : Geoffroy Andrieux
## Created     : 04/2010
## Revision    :
## Source      :
##
## Copyright 2010 : IRISA
##
## This library is free software; you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 2.1 of the License, or
## any later version.
##
## This library is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY, WITHOUT EVEN THE IMPLIED WARRANTY OF
## MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.  The software and
## documentation provided here under is on an "as is" basis, and IRISA has
## no obligations to provide maintenance, support, updates, enhancements
## or modifications.
## In no event shall IRISA be liable to any party for direct, indirect,
## special, incidental or consequential damages, including lost profits,
## arising out of the use of this software and its documentation, even if
## IRISA have been advised of the possibility of such damage.  See
## the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this library; if not, write to the Free Software Foundation,
## Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
##
## The original code contained here was initially developed by:
##
##     Geoffroy Andrieux.
##     IRISA/IRSET
##     Symbiose team
##     IRISA  Campus de Beaulieu
##     35042 RENNES Cedex, FRANCE
##
##
## Contributor(s): Michel Le Borgne, Nolwenn Le Meur
##
"""
Load and generate Cadbiom xml files
"""
from __future__ import unicode_literals
from __future__ import print_function

from cadbiom.models.guard_transitions.chart_model import ChartModel
from xml.sax import make_parser
from xml.sax import parseString as PS
from xml.sax.handler import ContentHandler
from lxml import etree
from lxml import objectify


class XmlVisitor:
    """Visitor used to generate xml cadbiom code when the model is exported."""

    def __init__(self, model):
        self.model_name = model.name
        self.model = model
        self.fact_list = []
        self.xml = ""      # string: xml representation of model
        self.symb = dict() # symbol table to check double naming of nodes
        self.visit_chart_model()

    def visit_chart_model(self):
        """
        Entrance point
        """
        self.visit_ctop_node(self.model.get_root())

#CNode:
#    def write_xml(self):
#        pass

    def check_name(self, name):
        """
        Detect double declarations
        """
        try:
            self.symb[name]
        except:
            self.symb[name] = "ok"
            return
        raise XmlException("Node double declaration")

    def visit_cstart_node(self, snode):
        """
        Generate xml representation of a start node
        """

        tag = "CStartNode"
        attrname = ["name", "xloc", "yloc"]

        attr = [snode.name, snode.xloc, snode.yloc]
        return [tag, attrname, attr]

    def visit_ctrap_node(self, tnode):
        """
        Generate xml representation of a trap node
        """
        tag = "CTrapNode"
        attrname = ["name", "xloc", "yloc"]
        attr = [tnode.name, tnode.xloc, tnode.yloc]
        return [tag, attrname, attr]

    def visit_csimple_node(self, sin):
        """
        Generate xml representation of a simple node
        """
        self.check_name(sin.name)
        tag = "CSimpleNode"
        attrname = ["name", "xloc", "yloc"]
        attr = [sin.name, sin.xloc, sin.yloc]
        return [tag, attrname, attr]

    def visit_cperm_node(self, pnode):
        """
        Generate xml representation of a perm node
        """
        self.check_name(pnode.name)
        tag = "CPermNode"
        attrname = ["name", "xloc", "yloc"]
        attr = [pnode.name, pnode.xloc, pnode.yloc]
        return [tag, attrname, attr]

    def visit_cinput_node(self, inn):
        """
        Generate xml representation of an input node
        """
        # double declaration of input nodes is allowed"
        tag = "CInputNode"
        attrname = ["name", "xloc", "yloc"]
        attr = [inn.name, inn.xloc, inn.yloc]
        return [tag, attrname, attr]


    def visit_cmacro_node(self, mnode):
        """
        Generate xml representation of a macro node
        """
        self.check_name(mnode.name)
        save_macro = self.current_element
        tag = "CMacroNode"
        attrname = ["name", "xloc", "yloc", "wloc", "hloc"]
        attr = [mnode.name, mnode.xloc, mnode.yloc, mnode.wloc, mnode.hloc]
        properties = [tag, attrname, attr]

        macro = etree.SubElement(self.current_element, properties[0])
        self.current_element = macro
        if len(properties) > 1:
            attrname = properties[1]
            attr = properties[2]
            attributes = macro.attrib
            for i in range(0, len(attrname)):
                attributes[attrname[i]] =  str(attr[i])

        # nodes
        for snode in mnode.sub_nodes:
            properties = snode.accept(self)
            if properties[0] == 'CMacroNode':
                self.current_element = macro

            if properties[0] != 'CMacroNode':
                subel = etree.SubElement(self.current_element, properties[0])
                if len(properties) > 1:
                    attrname = properties[1]
                    attr = properties[2]
                    attributes = subel.attrib
                    for i in range(0, len(attrname)):
                        attributes[attrname[i]] =  str(attr[i])

        # transitions
        for gtr in mnode.transitions:
            for trunlist in gtr:
                properties = trunlist.accept(self)
                sub_tr = etree.SubElement(self.current_element, properties[0])
                if len(properties) > 1:
                    attrname = properties[1]
                    attr = properties[2]
                    attributes = sub_tr.attrib
                    for i in range(0, len(attrname)):
                        attributes[attrname[i]] =  str(attr[i])
        self.current_element = save_macro
        return [tag, attrname, attr]

    def visit_ctop_node(self, tnode):
        """
        interative build of xml tree for model saving
        """
        header = objectify.ElementMaker(
            annotate=False,
            namespace="http://cadbiom.genouest.org/",
            nsmap={None : "http://cadbiom.genouest.org/"}
        )
        xmodel = header.model(name=self.model_name)
        self.current_element = xmodel

        def create_xml_element(entity):
            """Create XML element and add it to root object"""
            # get node or transition properties
            properties = entity.accept(self)
            if properties[0] != 'CMacroNode':
                element = etree.Element(properties[0])
                if len(properties) > 1:
                    attrname = properties[1]
                    attr = properties[2]
                    attributes = element.attrib
                    # Set attributes and values (name, event, coords...)
                    for i in range(0, len(attrname)):
                        attributes[attrname[i]] = str(attr[i])
                # Add notes/text of element
                if entity.note:
                    element.text = entity.note
                # Attach element to the model
                xmodel.append(element)

        # nodes
        for snode in tnode.sub_nodes:
            create_xml_element(snode)

        # transitions
        for gtr in tnode.transitions:
            for trans in gtr:
                create_xml_element(trans)

        # constraints
        if len(tnode.model.constraints) > 0:
            const = etree.Element("constraints")
            const.text = tnode.model.constraints
            xmodel.append(const)

        self.xml = etree.tostring(xmodel, pretty_print=True)
#        print (etree.tostring(xmodel,pretty_print=True))


    def visit_ctransition(self, trans):
        """
        Generate xml representation of a transition
        """
        tag = "transition"
        attrname = ["name", "ori", "ext", "event",
                    "condition", "action", "fact_ids"]
        attr = [trans.name, trans.ori.name, trans.ext.name, trans.event,
                trans.condition, trans.action, trans.fact_ids]

        fact_ids = trans.fact_ids
        for fact in fact_ids:
            self.fact_list.append(fact)

        return [tag, attrname, attr]

    def return_xml(self):
        """Return the model as xml string.

        .. note:: Used when the model is saved in a .bcx file.
        """
        return self.xml

    def get_fact_ids(self):
        """
        get litterature references
        """
        model_fact = []
        for i in self.fact_list:
            if i in model_fact:
                continue
            else :
                model_fact.append(i)
        return model_fact


class MakeHandler(ContentHandler):
    """Make a handler for the parser when the model is loaded.

    Users are expected to subclass ContentHandler to support their application.
    The following methods are called by the parser on the appropriate events
    in the input document:

    https://docs.python.org/2/library/xml.sax.handler.html
    """

    def __init__(self, model = None):
        self.pile_node = []
        self.top_pile = None
        self.pile_dict = []
        self.node_dict = dict()
        self.in_constraints = False
        self.constraints = ""
        self.model = model
        self.nodes_types = (
            'CStartNode', 'CTrapNode', 'CSimpleNode', 'CPermNode', 'CInputNode'
        )
        # Memorize the current node/transition because of inner text (note)
        # processing
        self.current_element = None

    def init_node_functions(self):
        """Bind functions to add different types of nodes to the cadbiom model

        .. note:: Must be call after the init of self.top_pile with the xml root
            object.
        """
        self.add_node_functions = \
            {
                'CStartNode': self.top_pile.add_start_node,
                'CTrapNode': self.top_pile.add_trap_node,
                'CSimpleNode': self.top_pile.add_simple_node,
                'CPermNode': self.top_pile.add_perm_node,
                'CInputNode': self.top_pile.add_input_node,
            }

    def startElement(self, name, att):
        """Signal the start of an element

        .. notes:: Nodes have to be at the top of the model (Before transitions)
            Transitions do not allow reflexive ones
            (as it could be said in the doc);
            Duplication of transitions are not authorized but only print a
            warning in the shell (they are not taken into account)

        :param arg1: Contains the raw XML 1.0 name of the element.
        :param arg2: Holds an object of the Attributes interface.
        :type arg1: <str>
        :type arg2: <xml.sax.xmlreader.AttributesImpl>
        """
        #print(att.getNames())

        if name in self.nodes_types:
            # TODO: Uniformization of API in CMacroNode() class;
            # the attribute 'name' should be at the same last position...
            element_name = att.get('name', '').encode('ascii')
            self.current_element = self.add_node_functions[name](
                name=element_name,
                xcoord=float(att.get('xloc', '0')),
                ycoord=float(att.get('yloc', '0')),
            )
            self.node_dict[element_name] = self.current_element

        elif name == "transition":
            name = att.get('name', '').encode('ascii')
            ori = att.get('ori', '')
            ext = att.get('ext', '')
            event = att.get('event', '')
            condition = att.get('condition', '')
            action = att.get('action', '')
            fact_ids_text = att.get('fact_ids','')[1:-1]
            if len(fact_ids_text) > 0:
                fact_ids = [int(id) for id in fact_ids_text.split(',')]
            else:
                fact_ids = []

            # Get nodes involved in the transition
            # If not present, raise an exception
            # => nodes have to be at the top of the model
            try:
                node_ori = self.node_dict[ori]
                node_ext = self.node_dict[ext]
            except Exception as exc:
                print('Bad xml file - missing nodes', ori, ' -> ', ext)
                print(self.node_dict)
                print(exc)

            self.current_element = self.top_pile.add_transition(node_ori, node_ext)
            # The transition may not be created (origin = ext for example)
            # /!\ Transitions do not allow reflexive ones
            # (as it could be said in the doc)
            # Duplication of transitions are not authorized but only print a
            # warning in the shell (they are not taken into account)
            if self.current_element:
                self.current_element.set_event(event)
                self.current_element.set_condition(condition)
                self.current_element.set_action(action)
                self.current_element.fact_ids = fact_ids

        elif name == "CMacroNode":
            name = att.get('name', '').encode('ascii')
            xloc = float(att.get('xloc', '0') )
            yloc = float(att.get('yloc', '0') )
            wloc = float(att.get('wloc', '5') )
            hloc = float(att.get('hloc', '5') )

            node = self.top_pile.add_macro_subnode(name, xloc, yloc,
                                                   wloc, hloc)
            self.node_dict[name] = node

            self.pile_node.append(node)
            # symbol table put on stack to preserve macro scope for inputs
            new_node_dict = dict()
            self.pile_dict.append(new_node_dict)
            self.top_pile = node
            self.node_dict = new_node_dict

        elif name == 'constraints':
            self.in_constraints = True
            self.constraints = ""

        elif name == "model":
            if not self.model:
                self.model = ChartModel(att.get('name',''))
            # Root is a virtual macronode on top of the hierarchy.
            # A model can be a list of hierarchy grouped under this node.
            root = self.model.get_root()
            self.pile_node.append(root)
            self.top_pile = root
            self.init_node_functions()
            new_dict = dict()
            self.pile_dict.append(new_dict)
            self.node_dict = new_dict

    def characters(self, chr):
        """Receive notification of character data.

        The Parser will call this method to report each chunk of character data.
        SAX parsers may return all contiguous character data in a single chunk,
        or they may split it into several chunks;
        => we need to do a concatenation

        :param arg1: chunck of characters.
        :type arg1: <str>
        """
        # The current elem is a constraint, a transition or a node
        # print("all", self.current_element, '<'+chr+'>')
        if self.in_constraints:
            self.constraints += chr
        elif self.current_element:
            # node or transition is currently opened in startElement()
            self.current_element.note += chr

    def endElement (self, name):
        """Called when an elements ends

        .. note:: We handle only elements that need post processing like
            transitions and nodes: reset self.current_element that is used
            to load notes (inner text of xml object).
        """

        if name == 'transition' or name in self.nodes_types:
            # Close the current node or transition opened in startElement()
            self.current_element = None
        elif name == 'CMacroNode':
            #self.top_pile = self.pile_node.pop()
            self.pile_node.remove(self.top_pile)
            self.top_pile = self.pile_node[-1]
            #self.node_dict = self.pile_dict.pop()
            self.pile_dict.remove(self.node_dict)
            self.node_dict = self.pile_dict[-1]
        elif name == 'constraints':
            self.in_constraints = False
            self.model.constraints = self.constraints + '\n'
        #elif name == 'model':
        #    print(len([e for e in self.top_pile.transitions]))
        #    print(len(self.top_pile.new_transitions))


class MakeModelFromXmlFile:
    """
    parse a xml file
    """
    def __init__(self, xml_file, model = None):
        self.model = model
        self.handler = MakeHandler(model=self.model)
        self.parser = make_parser()
        self.parser.setContentHandler(self.handler)
        try:
            self.parser.parse(xml_file)
        except Exception:
            print('ERROR while xml parsing')
            raise


    def get_model(self):
        """
        As it says
        """
        return self.handler.model

class MakeModelFromXmlString:
    """
    parse a xml description as string
    """
    def __init__(self, xml_string):
        self.model = None
        self.handler = MakeHandler()
        self.parser = make_parser()
        self.parser.setContentHandler(self.handler)

        try:
            PS(xml_string, self.handler)
        except Exception as exc:
            print('ERROR while xml parsing')
            print(exc)


    def get_model(self):
        """
        As it says
        """
        return self.handler.model


class XmlException(Exception):
    """
    For exception identification
    """
    def __init__(self, mess):
        self.message = mess






















