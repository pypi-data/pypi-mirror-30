
"""
Functions to compile a set of CPPA3 documents into data structures that facilitate
efficient lookup at runtime for inbound or outbound message exchange.

For an Endpoint, compute the Channels that use them and from there the Actions bound
to them.

"""

import logging
logging.basicConfig(level=logging.DEBUG)

from copy import deepcopy

_NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
         'ds': 'http://www.w3.org/2000/09/xmldsig#',
         'xml': 'http://www.w3.org/XML/1998/namespace',
         'xkms': 'http://www.w3.org/2002/03/xkms#',
         'dsig11' : 'http://www.w3.org/2009/xmldsig11#'
         }

class InboundConfiguration():

    def __init__(self):

        self.channel_handlers = {
            cppa('ebMS3Channel') : self.register_ebms3_channel
        }
        self.loaded_cpas = {}

        self.incoming_channel_from_push_transport = {}
        self.incoming_channel_type_from_push_transport = {}

    def load_cpa(self, cpa):
        agreement_id = cpa.xpath(
            'cppa:AgreementInfo/cppa:AgreementIdentifier/text()',
            namespaces=_NSMAP)[0]
        self.loaded_cpas[agreement_id] = deepcopy(cpa)
        for party in cpa.xpath(
                'cppa:PartyInfo/cppa:PartyId',
                namespaces=_NSMAP
        ):
            for counterparty in cpa.xpath(
                    'cppa:CounterPartyInfo/cppa:PartyId',
                    namespaces=_NSMAP
            ):
                for service_specification in cpa.xpath(
                    'cppa:ServiceSpecification',
                    namespaces=_NSMAP
                ):
                    party_role = service_specification.xpath(
                        'cppa:PartyRole/@name',
                        namespaces=_NSMAP
                    )[0]
                    counterparty_role = service_specification.xpath(
                        'cppa:CounterPartyRole/@name',
                        namespaces=_NSMAP
                    )[0]
                    for service_binding in service_specification.xpath(
                        'cppa:ServiceBinding',
                        namespaces=_NSMAP
                    ):
                        service = service_binding.xpath(
                            'cppa:Service',
                            namespaces=_NSMAP
                        )[0]
                        for action_binding in service_binding.xpath(
                            'cppa:ActionBinding',
                            namespaces=_NSMAP
                        ):
                            self.register_action_binding(cpa, agreement_id,
                                                     party.text, party.get('type'),
                                                     counterparty.text, counterparty.get('type'),
                                                     party_role, counterparty_role,
                                                     service.text, service.get('type'),
                                                     action_binding)

    def register_action_binding(self, cpa,
                            agreement_id, party_id, party_id_type,
                            counterparty_id, counterparty_id_type,
                            party_role, counterparty_role,
                            service, service_type,
                            action_binding):

        action_binding_id = action_binding.get('id')
        direction = action_binding.get('sendOrReceive')
        action = action_binding.get('action')
        channel_id = action_binding.xpath(
            'cppa:ChannelId',
            namespaces=_NSMAP
        )[0].text
        payload_profile_id = action_binding.xpath(
            'cppa:PayloadProfileId/text()',
            namespaces=_NSMAP
        )
        if len(payload_profile_id) > 0:
            payload_profile_id = payload_profile_id[0]
        else:
            payload_profile_id = None

        logging.debug('{} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(
            agreement_id, action_binding_id, party_id, party_id_type,
            counterparty_id, counterparty_id_type,
            party_role, counterparty_role,
            service, service_type,
            action,
            direction,
            channel_id,
            payload_profile_id)
        )
        self.register_channel(cpa,
                              agreement_id, action_binding_id,
                              party_id, party_id_type,
                              counterparty_id, counterparty_id_type,
                              party_role, counterparty_role,
                              service, service_type,
                              action,
                              direction,
                              channel_id,
                              payload_profile_id)

    def register_channel(self, cpa,
                         agreement_id, action_binding_id,
                         party_id, party_id_type, counterparty_id, counterparty_id_type,
                         party_role, counterparty_role,
                         service, service_type, action, direction,
                         channel_id, pp_id):
        channel_el = cpa.xpath(
            'node()[@id="{}"]'.format(channel_id),
            namespaces=_NSMAP
        )[0]
        channel_type = channel_el.tag
        if channel_type not in self.channel_handlers:
            logging.info('Cannot handle channel type {}'.format(channel_type))
        else:
            handler = self.channel_handlers[channel_type]
            handler(cpa,
                    agreement_id, action_binding_id,
                    party_id, party_id_type, counterparty_id, counterparty_id_type,
                    party_role, counterparty_role,
                    service, service_type, action, direction,
                    channel_id, pp_id, channel_el)

    def register_ebms3_channel(self, cpa,
                         agreement_id, action_binding_id,
                         party_id, party_id_type, counterparty_id, counterparty_id_type,
                         party_role, counterparty_role,
                         service, service_type, action, direction,
                         channel_id, pp_id, channel_el):
        transport_id = channel_el.get('transport')
        if transport_id != None:
            transport_el = cpa.xpath(
                'node()[@id="{}"]'.format(transport_id)
            )[0]
            logging.debug('Transport id {}, type {}'.format(transport_id, transport_el.tag))
            endpoint = transport_el.xpath(
                'cppa:Endpoint', namespaces=_NSMAP
            )[0].text
            logging.debug('Push endpoint 1 {} 2 {} 3 {} 4 {} 5 {} 6 {}'.format(endpoint, channel_id,
                                                                          agreement_id, action_binding_id,
                                                                          channel_id, pp_id))
            self.incoming_channel_type_from_push_transport[endpoint] = cppa('ebMS3Channel')
            if endpoint not in self.incoming_channel_from_push_transport:
                self.incoming_channel_from_push_transport[endpoint] = {}
            channel_key = (
                agreement_id,
                party_id,
                party_id_type,
                party_role,
                counterparty_id,
                counterparty_id_type,
                counterparty_role,
                service,
                service_type,
                action )
            if channel_key not in self.incoming_channel_from_push_transport[endpoint]:
                self.incoming_channel_from_push_transport[endpoint][channel_key] = agreement_id, channel_id

        else:
            logging.info('@@@@ 13')
            """
             Other cases:
             -  Channel is a synchronous response channel
             -  Channel is a Pull response channel
            """



def cppa(el):
    return '{{{}}}{}'.format(_NSMAP['cppa'],el)

def xml(el):
    return '{{{}}}{}'.format(_NSMAP['xml'],el)
