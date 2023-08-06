from graphene import Node, String
from graphene_django import DjangoObjectType

from . import choices, models


class TermNode(DjangoObjectType):

    hpo_term = String()
    hpo_url = String()

    class Meta:
        model = models.Term
        interfaces = (Node, )

    def resolve_hpo_term(self, info):
        return self.hpo_term

    def resolve_hpo_url(self, info):
        return self.hpo_url


class VersionNode(DjangoObjectType):

    class Meta:
        model = models.Version
        interfaces = (Node, )


class SynonymNode(DjangoObjectType):

    scope = String()

    class Meta:
        model = models.Synonym
        interfaces = (Node, )

    def resolve_scope(self, info):
        if self.scope:
            return choices.SYNONYM_SCOPES[self.scope]


class CrossReferenceNode(DjangoObjectType):

    source = String()

    class Meta:
        model = models.CrossReference
        interfaces = (Node, )

    def resolve_source(self, info):
        return choices.CROSS_REFERENCES[self.source]


class DiseaseNode(DjangoObjectType):

    label = String()
    database = String()
    qualifier = String()
    evidence_code = String()
    database_url = String()
    hpo_mode_of_inheritance_url = String()
    hpo_age_of_onset_url = String()
    hpo_frequency_url = String()

    class Meta:
        model = models.Disease
        interfaces = (Node, )

    def resolve_label(self, info):
        return self.label

    def resolve_database(self, info):
        return choices.DATABASES[self.database]

    def resolve_qualifier(self, info):
        if self.qualifier:
            return choices.QUALIFIERS[self.qualifier]

    def resolve_evidence_code(self, info):
        if self.evidence_code:
            return choices.EVIDENCE[self.evidence_code]

    def resolve_database_url(self, info):
        return self.database_url

    def resolve_hpo_mode_of_inheritance_url(self, info):
        return self.hpo_mode_of_inheritance_url

    def resolve_hpo_age_of_onset_url(self, info):
        return self.hpo_age_of_onset_url

    def resolve_hpo_frequency_url(self, info):
        return self.hpo_frequency_url
