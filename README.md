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


