# Sistema Escolar — Spring Boot

**Aluno:** Gabriel Pinheiro Rodrigues da Silva

**Atividade:** Ciclo avaliativo 1 — Caça aos 8 erros

API REST para cadastrar professores e alunos e registrar matrículas, desenvolvida com Java 17, Spring Boot 4.0.5, Spring Data JPA e H2 em memória.

Projeto base: https://github.com/Will-firmino/sistema_escolar_java

## Os 8 erros e suas correções

Os caminhos Java abaixo são relativos a `src/main/java/com/github/app/`.
Na coluna de identificação, as mensagens entre crases representam o tipo de falha esperado pelo código original; não são transcrições de logs coletados antes de cada correção.

| Nº | Arquivo | O que estava errado | Como identificar | Correção |
| --- | --- | --- | --- | --- |
| 1 | `pom.xml` | H2 tinha escopo `test`, ficando fora do classpath da aplicação executada normalmente. | A URL configurada usa H2, mas o driver não está disponível ao subir a aplicação (`Cannot load driver class: org.h2.Driver` ou falha de configuração do datasource). | Alterar o escopo para `runtime`. |
| 2 | `src/main/resources/application-test.properties` | `spring.jpa.hibernate.ddl-auto=none` não criava as tabelas no banco em memória. | Em um banco novo, consultas e cadastros encontram tabelas inexistentes (`Table ... not found`). O perfil ativo é `test`. | Usar `create-drop`, criando o esquema na inicialização e removendo no encerramento. O banco continua em memória e reinicia vazio. |
| 3 | `model/professor/Professor.java` | O campo `id` tinha apenas `@Id`, sem geração automática. | Cadastro de professor sem ID exige atribuição manual do identificador (`Identifier ... must be manually assigned`). | Adicionar `@GeneratedValue(strategy = GenerationType.IDENTITY)`. |
| 4 | `controller/ProfessorController.java` | A rota base era `/professor`, no singular. | As requisições exigidas para `/professores` não encontram o controller (404). | Alterar `@RequestMapping` para `/professores`. |
| 5 | `model/aluno/Aluno.java` | O construtor preenchia `ra` com `dados.curso()`. | Cadastrar RA `2026001` e curso `ADS` fazia a listagem mostrar `ADS` também no RA. | Atribuir `this.ra = dados.ra()`. |
| 6 | `controller/AlunoController.java` | O método PUT alterava a entidade sem uma transação que persistisse as mudanças. | O PUT podia responder sem erro, mas um GET posterior mantinha o curso antigo. | Adicionar `@Transactional` ao método `atualizar`, permitindo o dirty checking do JPA ao concluir a transação. |
| 7 | `model/matricula/DadosCadastroMatricula.java` e `controller/MatriculaController.java` | O DTO esperava `idAluno`, enquanto o JSON do contrato envia `alunoId`. | O JSON informado no enunciado deixava o identificador do aluno nulo, causando falha na busca da referência. | Renomear o componente para `alunoId` e usar `dados.alunoId()` no controller. Os dois arquivos compõem a mesma correção do contrato. |
| 8 | `model/matricula/Matricula.java` | A relação com aluno era `@OneToOne`, impondo unicidade ao aluno nas matrículas. | A segunda matrícula para o mesmo aluno violava a restrição única, mesmo usando outro turno. | Trocar para `@ManyToOne`, permitindo várias matrículas para um aluno. |

## Como executar

Requisitos: JDK 17 ou superior e acesso à internet para o Maven baixar as dependências. Não é necessário instalar MySQL nem configurar autenticação.

Abra o terminal na pasta que contém o `pom.xml`.

Windows (PowerShell ou CMD):

```powershell
.\mvnw.cmd spring-boot:run
```

Linux/macOS:

```bash
bash mvnw spring-boot:run
```

A API ficará em `http://localhost:8080`. O perfil `test` já está ativo em `application.properties`. Os dados são temporários: o banco H2 é recriado vazio a cada inicialização.

## Endpoints

| Recurso | Operações |
| --- | --- |
| Professores | `POST /professores`, `GET /professores`, `GET /professores/listar`, `GET /professores/todos`, `PUT /professores`, `DELETE /professores/{id}` |
| Alunos | `POST /alunos`, `GET /alunos`, `GET /alunos/listar`, `GET /alunos/todos`, `PUT /alunos`, `DELETE /alunos/{id}` |
| Matrículas | `POST /matriculas`, `GET /matriculas`, `DELETE /matriculas/{id}` |

Use `Content-Type: application/json` nos POST e PUT. As rotas GET de professores e alunos sem sufixo aceitam paginação, por exemplo `?page=0&size=10`. Os IDs são gerados pelo banco; consulte `/todos` após cadastrar. Os POST, PUT e DELETE mantêm o retorno vazio do projeto base.

Exemplo de professor:

```json
{"nome":"Ana Souza","email":"ana.souza@escola.com","telefone":"21999990000","registro":"PRF-1001","disciplina":"MATEMATICA","endereco":{"logradouro":"Rua das Flores","bairro":"Centro","cep":"20000000","cidade":"Rio de Janeiro","uf":"RJ"}}
```

Exemplo de aluno:

```json
{"nome":"Bruno Lima","email":"bruno.lima@escola.com","telefone":"21988880000","ra":"2026001","curso":"ADS","endereco":{"logradouro":"Av. Brasil","bairro":"Penha","cep":"21000000","cidade":"Rio de Janeiro","uf":"RJ"}}
```

Exemplo de matrícula (substitua os IDs pelos cadastrados):

```json
{"alunoId":1,"professorId":1,"turno":"MANHA","semestre":"2026.2","observacao":"Turma A"}
```

Repita com `turno` igual a `NOITE` para conferir duas matrículas do mesmo aluno. Os turnos aceitos são `MANHA`, `TARDE` e `NOITE`. Sem `dataMatricula`, a aplicação usa a data e a hora atuais.

Exemplos de atualização parcial:

```json
{"id":1,"email":"ana.nova@escola.com"}
```

Envie o JSON acima para `PUT /professores`. Para `PUT /alunos`:

```json
{"id":1,"curso":"Engenharia de Software"}
```

Confirme as alterações com um novo GET. Exclua primeiro as matrículas antes dos alunos e professores referenciados, respeitando as chaves estrangeiras.

## Testes

Teste de inicialização do Spring:

```powershell
.\mvnw.cmd test
```

No Linux/macOS: `bash mvnw test`.

Com a API iniciada e o banco vazio, execute o teste funcional (Python 3, sem bibliotecas externas):

```bash
python scripts/testar_api.py
```

O script testa todos os endpoints exigidos, confere o RA e os IDs, compara listagens e paginação, verifica atualizações em requisições posteriores, cria duas matrículas do mesmo aluno, confere datas automática e explícita e exclui os registros. Ele cria e remove apenas seus dados de teste e exige banco vazio no começo.

### Resultado da verificação

- `mvnw test`: 1 teste, 0 falhas, 0 erros (`BUILD SUCCESS`).
- Aplicação iniciada com Java 17 e as dependências resolvidas pelo Maven.
- `scripts/testar_api.py`: 28 requisições HTTP concluídas, com todas as verificações passando.
- As 8 correções foram mantidas no escopo do enunciado; o script funcional é um apoio adicional à conferência pelo Postman/Insomnia.
