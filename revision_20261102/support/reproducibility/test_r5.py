import unittest
from r5_engine import Config,Engine,project,with_lineage,identifier_parts,label_hypothesis

def baseline(key='B1',code='长82-1',source='延河1号',layer='长82'):
    return dict(baseline_id=key,sample_id_raw=code,sample_id_norm=code,outcrop_raw=source,strat_unit_norm=layer,lithology_norm='砂岩')
def query(code='长82-1',source='延河1号',layer='',**kw):
    return dict(record_key='Q1',record_id='Q1',family='grain_size',sample_id_raw=code,sample_id_norm=code,strat_unit_norm=layer,lithology_norm='砂岩',document=dict(detail_source=source,detail_layer=layer,**kw))
class Tests(unittest.TestCase):
    def test_plain_identifier_carries_layer_even_when_field_empty(self):
        f=with_lineage(project(query()));self.assertEqual((f['explicit_layer'],f['coded_layer']),('','长82'))
        self.assertFalse(f['layer_evidence'][0]['independent_of_identifier'])
    def test_original_observation_not_overwritten(self):
        q=query();Engine([baseline()]).recover(q);self.assertEqual(q['document']['detail_layer'],'')
    def test_subsample_tail_preserved(self):
        z=identifier_parts('10-长61-2-1','xrf');self.assertEqual(z['coded_layer'],'长61');self.assertIn('长61-2-1',z['aliases'])
    def test_plain_code_rule_no_invented_layer_for_Y(self):
        self.assertEqual(identifier_parts('Y2-1','thin_section')['coded_layer'],'')
    def test_C_scope_limited(self):
        self.assertEqual(identifier_parts('1-C82-1','xrf')['coded_layer'],'')
        self.assertEqual(identifier_parts('1-C82-1','hyperspectral')['coded_layer'],'长82')
    def test_no_identifier_erases_all_derived_channels(self):
        q=query('1-C82-1',source='',layer='');q['family']='hyperspectral';f=project(q,Config(identifier=False))
        for k in ['raw_identifier','normalized_identifier','coded_layer','coded_layer_rule','source_number']:self.assertFalse(f[k],k)
        self.assertEqual(f['identifier_aliases'],[])
    def test_no_identifier_keeps_explicit_layer(self):
        f=project(query(layer='长82'),Config(identifier=False));self.assertEqual(f['explicit_layer'],'长82');self.assertFalse(f['coded_layer'])
    def test_no_strat_erases_both_layer_channels(self):
        f=project(query(layer='长82'),Config(stratigraphy=False));self.assertFalse(f['explicit_layer']);self.assertFalse(f['coded_layer']);self.assertFalse(f['layer_evidence'])
        self.assertEqual(f['normalized_identifier'],'长82-1')
    def test_no_source_erases_prefix_source(self):
        f=project(query('1-长82-1'),Config(source=False));self.assertFalse(f['source_number']);self.assertFalse(f['named_source']);self.assertFalse(f['source_fields'])
    def test_alias_ablation_does_not_disable_plain_layer_parser(self):
        self.assertEqual(project(query(),Config(alias=False))['coded_layer'],'长82')
        q=query('1-C82-1');q['family']='hyperspectral';self.assertFalse(project(q,Config(alias=False))['coded_layer'])
    def test_layer_disagreement_not_silently_resolved(self):
        f=project(query(layer='长61'));self.assertIn('coded_explicit_layer_disagreement',f['flags']);self.assertEqual(f['coded_layer'],'长82');self.assertEqual(f['explicit_layer'],'长61')
    def test_no_strat_drops_layer_disagreement_gate(self):
        self.assertNotIn('coded_explicit_layer_disagreement',project(query(layer='长61'),Config(stratigraphy=False))['flags'])
    def test_no_identifier_drops_identifier_gate(self):
        self.assertNotIn('document_identifier_disagreement',project(query(identifier_disagreement=True),Config(identifier=False))['flags'])
    def test_granularity_not_guessed(self):
        f=project(query(layer='长8'));self.assertIn('coded_explicit_layer_granularity_unresolved',f['review']);self.assertNotIn('coded_explicit_layer_disagreement',f['flags'])
    def test_cross_outcrop_repeat_preserved(self):
        e=Engine([baseline(),baseline('B2',source='延河2号')]);self.assertEqual(e.recover(query())['candidate_ids'],['B1'])
    def test_same_layer_not_sufficient_to_confirm_identity(self):
        r=Engine([baseline()]).recover(query('长82-9'));self.assertIsNone(r['native_accept']);self.assertEqual(r['independent_physical_reference'],'unknown')
    def test_region_and_outcrop_code_not_automatically_distinct(self):
        f=project(query('Y2-1',source='Y2',catalogue_source='八道湾'));self.assertIn('source_naming_scope_unresolved',f['review']);self.assertNotIn('document_comparable_source_disagreement',f['flags'])
    def test_comparable_source_conflict_still_held(self):
        r=Engine([baseline()]).recover(query(source='延河1号',catalogue_source='延河2号'));self.assertTrue(r['documentary_hold'])
    def test_display_group_does_not_assert_physical_identity(self):
        a=label_hypothesis(project(query()));b=label_hypothesis(project(query(layer='长82')))
        self.assertEqual(a,b);self.assertFalse(a['physical_identity_confirmed'])
    def test_duplicate_technical_keys_rejected(self):
        with self.assertRaises(ValueError):Engine([baseline(),baseline()])
    def test_numeric_id_layer_alias_has_strat_dependency(self):
        q=query('1',layer='长82');self.assertIn('长82-1',project(q)['identifier_aliases'])
        self.assertNotIn('长82-1',project(q,Config(stratigraphy=False))['identifier_aliases'])

if __name__=='__main__':unittest.main(verbosity=2)
