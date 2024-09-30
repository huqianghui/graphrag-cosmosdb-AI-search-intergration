doc_import_gremlin_query = """
g.V().hasLabel('__Document__').has('id', id)
  .fold()
  .coalesce(
    unfold(),  // if exists
    addV('__Document__').property('id', id).property('vertex_id', vertex_id)  // if not exists
  )
  .property('title', title)
  .property(single, 'raw_content', raw_content)
  .property(single, 'text_unit_ids', text_unit_ids)
"""

chunk_import_gremlin_query = """
            g.V().hasLabel('__Chunk__').has('id', id).fold().coalesce(
                unfold(),
                addV('__Chunk__').property('id', id).property('vertex_id', vertex_id)
            ).property('text', text).property('n_tokens', n_tokens)
            """

chunk_doc_relation_gremlin_query = """
                g.V().hasLabel('__Chunk__').has('id', chunk_id).as('c')
                .V().hasLabel('__Document__').has('id', doc_id).as('d')
                .coalesce(
                    select('d').identity(),
                    __.constant('Error: Document not found')
                )
                .coalesce(
                    select('c').outE('PART_OF').where(inV().as('d')),
                    select('c').addE('PART_OF').to('d')
                )
                """

entity_import_gremlin_query = """
            g.V().hasLabel('__Entity__').has('id', id).fold().coalesce(
                unfold(),
                addV('__Entity__').property('id', id).property('vertex_id', vertex_id))
                .property('name', name)
                .property('type', type)
                .property('description', description)
                .property('human_readable_id', human_readable_id)
            """

entity_text_unit_relation_gremin_query = """
                g.V().hasLabel('__Entity__').has('id', entity_id).as('c')
                .V().hasLabel('__Chunk__').has('id', text_unit_id).as('d')
                .coalesce(
                    select('d').identity(),
                    __.constant('Error: text_unit not found')
                )
                .coalesce(
                    select('d').outE('HAS_ENTITY').where(inV().as('c')),
                    select('d').addE('HAS_ENTITY').to('c')
                )
                """

entity_realtion_import_grelin_query = """
             g.V().hasLabel('__Entity__').has('name', source)
                    .as('source')
                    .V().hasLabel('__Entity__').has('name', target)
                    .as('target')
                    .coalesce(
                    __.inE().where(outV().as('source')),
                    addE('RELATED').from('source').to('target').property('id', id)
                    )
                    .property('rank', rank)  
                    .property('weight', weight)  
                    .property('human_readable_id', human_readable_id)  
                    .property('description', description)  
                    .property('text_unit_ids', text_unit_ids)  
            """

community_import_grelin_query = """
            g.V().hasLabel('__Community__').has('id', id)
                .fold()
                .coalesce(
                    unfold(),
                    addV('__Community__').property('id', id).property('vertex_id', vertex_id)
                )
                .property('level', level)
                .property('title', title)
            """

entity_community_rel_grelin_query = """
                g.E().hasLabel('RELATED').hasId(relationship_id)
                    .bothV().hasLabel('__Entity__').dedup()  
                    .as('entity')
                    .V().hasLabel('__Community__').hasId(community_id)
                    .as('community')
                    .coalesce(
                        select('entity').outE('IN_COMMUNITY').where(inV().as('community')),  
                        select('entity').addE('IN_COMMUNITY').to('community')  
                    )
                """

community_report_merge_grelin_query = """
            g.V().has('__Community__', 'id', id)
                .fold()
                .coalesce(
                    unfold(),
                    addV('__Community__').property('id', id)
                        .property('vertex_id', vertex_id))
                .property('level', level)
                .property('title', title)
                .property('rank', rank)
                .property('rank_explanation', rank_explanation)
                .property('full_content', full_content)
                .property('summary', summary)
            """

community_finding_import_grelin_query = """
                g.V().has('__Finding__', 'id', id)  
                    .fold()  
                    .coalesce(  
                        unfold(),  
                        addV('__Finding__').property('id', id).property('vertex_id', id)  
                    )  
                    .property('explanation', explanation)  
                    .property('summary', summary)  
                """

community_having_finding_grelin_query = """
                g.V().has('__Community__', 'id', communityId)  
                    .as('c')  
                    .V().has('__Finding__', 'id', id)  
                    .coalesce(  
                        inE('HAS_FINDING').where(outV().as('c')),  
                        addE('HAS_FINDING').from('c')  
                    )
                """

community_entity_count_grelin_query = ''' 
        g.V().hasLabel('__Community__')
        .as('community')
        .in('IN_COMMUNITY')
        .in('HAS_ENTITY')
        .groupCount()
        .by(select('community'))
    '''

community_weight_update_query = '''
        g.V(community_id).property('weight', chunkCount)
        '''