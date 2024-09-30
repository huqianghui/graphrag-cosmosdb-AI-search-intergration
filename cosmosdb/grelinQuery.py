# text unit grelin string
cosmosDB_text_mapping_grelin_query_template = '''
g.V({entity_ids})
  .as('n')  
  .in('HAS_ENTITY')
  .hasLabel('__Chunk__')  
  .group()
  .by(values('text'))
  .by(select('n').dedup().count())
  .order(local).by(values, Order.decr)
  .limit(local, {chunk})
  .as('text_mapping')
'''

# community summary grelin string
cosmosDB_community_grelin_query_template = '''
g.V({entity_ids})
  .as('n')
 .out('IN_COMMUNITY')
 .hasLabel('__Community__')
 .dedup()
 .project('summary', 'rank', 'weight')
 .by('summary')
 .by('rank')
 .by('weight')
 .order()
  .by(select('rank'))
  .by(select('weight'),Order.decr)
 .limit({community})
 .select('summary')
'''

# entity relation outside grelin string
cosmosDB_outside_relation_grelin_query_template = '''
g.V({entity_ids})
 .as('startNode')
 .bothE('RELATED')
 .where(otherV().not(hasId(within({entity_ids}))))
 .dedup()
 .project('descriptionText', 'rank', 'weight')
 .by('description')
 .by('rank')
 .by('weight')
 .order()
  .by(select('rank'))
  .by(select('weight'),Order.decr)
 .limit({relation})
 .select('descriptionText')
'''

# entity relation inside grelin string
cosmosDB_inside_relation_grelin_query_template = '''
g.V({entity_ids})
.as('startNode')
 .bothE('RELATED')
 .where(otherV().hasId(within({entity_ids})))
  .dedup()
 .project('descriptionText', 'rank', 'weight')
 .by('description')
 .by('rank')
 .by('weight')
 .order()
  .by(select('rank'))
  .by(select('weight'),Order.decr)
 .limit({relation})
 .select('descriptionText')
'''

