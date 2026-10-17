package com.github.app.model.matricula;

import java.time.LocalDateTime;

import jakarta.validation.constraints.NotNull;

public record DadosCadastroMatricula(

    @NotNull
    Integer alunoId,

    @NotNull
    Integer professorId,

    @NotNull
    Turno turno,

    String semestre,

    String observacao,

    LocalDateTime dataMatricula
) {
}
