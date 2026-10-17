"""Teste funcional: execute com a aplicação rodando e banco vazio.
Uso: python scripts/testar_api.py [http://localhost:8080]
"""
import json
import sys
from urllib.request import Request, urlopen

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8080'
checks = 0


def request(method, path, body=None):
    global checks
    data = json.dumps(body).encode() if body is not None else None
    req = Request(BASE + path, data=data, method=method,
                  headers={'Content-Type': 'application/json'})
    with urlopen(req, timeout=15) as response:
        assert 200 <= response.status < 300
        raw = response.read()
        checks += 1
        print(f'OK {method} {path}')
        return json.loads(raw) if raw else None


address = dict(logradouro='Rua das Flores', bairro='Centro', cep='20000000',
               cidade='Rio de Janeiro', uf='RJ')
assert request('GET', '/professores/todos') == [], 'Use um banco vazio'
assert request('GET', '/alunos/todos') == [], 'Use um banco vazio'
request('POST', '/professores', dict(nome='Ana Souza', email='ana@escola.com',
        telefone='21999990000', registro='PRF-1001', disciplina='MATEMATICA', endereco=address))
request('POST', '/alunos', dict(nome='Bruno Lima', email='bruno@escola.com',
        telefone='21988880000', ra='2026001', curso='ADS', endereco=address))
p = request('GET', '/professores/todos')[0]
a = request('GET', '/alunos/todos')[0]
assert isinstance(p['id'], int) and isinstance(a['id'], int)
assert a['ra'] == '2026001' and a['curso'] == 'ADS'
for resource in ('professores', 'alunos'):
    rows = request('GET', '/' + resource + '/listar')
    page = request('GET', '/' + resource + '?page=0&size=10')
    assert rows == page['content'] and len(rows) == 1
request('PUT', '/professores', dict(id=p['id'], nome='Ana Atualizada',
        email='ana.nova@escola.com', telefone='2100000000', endereco={'bairro': 'Icarai'}))
request('PUT', '/alunos', dict(id=a['id'], nome='Bruno Atualizado',
        curso='Engenharia de Software', telefone='2111111111', endereco={'cidade': 'Niteroi'}))
p2 = request('GET', '/professores/todos')[0]
a2 = request('GET', '/alunos/todos')[0]
assert p2['email'] == 'ana.nova@escola.com' and p2['nome'] == 'Ana Atualizada'
assert p2['telefone'] == '2100000000' and p2['endereco']['bairro'] == 'Icarai'
assert p2['registro'] == 'PRF-1001' and p2['endereco']['cep'] == '20000000'
assert a2['curso'] == 'Engenharia de Software' and a2['nome'] == 'Bruno Atualizado'
assert a2['telefone'] == '2111111111' and a2['endereco']['cidade'] == 'Niteroi'
assert a2['ra'] == '2026001' and a2['email'] == 'bruno@escola.com'
for turno in ('MANHA', 'NOITE'):
    body = dict(alunoId=a['id'], professorId=p['id'], turno=turno,
                semestre='2026.2', observacao='Turma A')
    if turno == 'NOITE':
        body['dataMatricula'] = '2026-10-17T10:30:00'
    request('POST', '/matriculas', body)
rows = request('GET', '/matriculas')
assert len(rows) == 2 and len({m['id'] for m in rows}) == 2
assert {m['turno'] for m in rows} == {'MANHA', 'NOITE'}
for m in rows:
    assert m['aluno']['id'] == a['id'] and m['professor']['id'] == p['id']
    assert m['dataMatricula'] and m['semestre'] == '2026.2' and m['observacao'] == 'Turma A'
    if m['turno'] == 'NOITE':
        assert m['dataMatricula'].startswith('2026-10-17T10:30:00')
    request('DELETE', f"/matriculas/{m['id']}")
assert request('GET', '/matriculas') == []
for resource, item in [('alunos', a), ('professores', p)]:
    request('DELETE', f"/{resource}/{item['id']}")
    assert request('GET', '/' + resource + '/todos') == []
    assert request('GET', '/' + resource + '/listar') == []
    assert request('GET', '/' + resource)['content'] == []
print(f'{checks} requisições passaram; cadastros, listagens, atualizações e exclusões conferidos.')
