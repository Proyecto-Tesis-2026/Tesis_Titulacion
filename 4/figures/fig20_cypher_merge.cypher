// Upsert idempotente de fragmentos y relaciones
// Lee desde Postgres (analisis_llm) y escribe en Neo4j
UNWIND rows AS row
MERGE (d:Documento {id: row.documento_id})
  ON CREATE SET d.fuente = row.fuente,
                d.publicado_en = datetime(row.publicado_en)
MERGE (f:Fragmento {id: row.fragmento_id})
  ON CREATE SET f.texto = row.texto,
                f.fecha = datetime(row.fecha)
MERGE (d)-[:CONTIENE]->(f)
WITH f, row
UNWIND row.candidatos AS c
  MERGE (cd:Candidato {id: c.id})
  MERGE (f)-[m:MENCIONA]->(cd)
    SET m.sentimiento = c.sentimiento,
        m.rol = c.rol
WITH f, row
MERGE (t:Tema {id: row.tema_id})
MERGE (f)-[r:SOBRE_TEMA]->(t)
  SET r.sentimiento = row.sentimiento_tema,
      r.confianza = row.confianza
