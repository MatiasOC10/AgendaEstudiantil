#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX 50

typedef struct {
    char nombre[50];
    char docente[50];
    int unidades;
} Materia;


typedef struct {
    char titulo[50];
    char fecha[20];
} Tarea;


typedef struct {
    char materia[50];
    char fecha[20];
} Examen;


Materia materias[MAX];
Tarea tareas[MAX];
Examen examenes[MAX];

int cantidadMaterias = 0;
int cantidadTareas = 0;
int cantidadExamenes = 0;



void registrarMateria(){

    printf("\n--- NUEVA MATERIA ---\n");

    printf("Nombre: ");
    scanf(" %[^\n]", materias[cantidadMaterias].nombre);

    printf("Docente: ");
    scanf(" %[^\n]", materias[cantidadMaterias].docente);

    printf("Unidades: ");
    scanf("%d",&materias[cantidadMaterias].unidades);

    cantidadMaterias++;

    printf("Materia registrada correctamente\n");
}



void mostrarMaterias(){

    printf("\n--- MATERIAS ---\n");

    for(int i=0;i<cantidadMaterias;i++){

        printf("\nMateria: %s", materias[i].nombre);
        printf("\nDocente: %s", materias[i].docente);
        printf("\nUnidades: %d\n", materias[i].unidades);

    }

}



void registrarTarea(){

    printf("\n--- NUEVA TAREA ---\n");

    printf("Titulo: ");
    scanf(" %[^\n]", tareas[cantidadTareas].titulo);

    printf("Fecha entrega: ");
    scanf("%s", tareas[cantidadTareas].fecha);


    cantidadTareas++;

    printf("Tarea registrada\n");

}



void mostrarTareas(){

    printf("\n--- TAREAS ---\n");


    for(int i=0;i<cantidadTareas;i++){

        printf("\nTitulo: %s", tareas[i].titulo);
        printf("\nFecha: %s\n", tareas[i].fecha);

    }

}



void registrarExamen(){

    printf("\n--- NUEVO EXAMEN ---\n");


    printf("Materia: ");
    scanf(" %[^\n]", examenes[cantidadExamenes].materia);


    printf("Fecha: ");
    scanf("%s", examenes[cantidadExamenes].fecha);


    cantidadExamenes++;

    printf("Examen registrado\n");

}



void mostrarExamenes(){

    printf("\n--- EXAMENES ---\n");


    for(int i=0;i<cantidadExamenes;i++){

        printf("\nMateria: %s", examenes[i].materia);
        printf("\nFecha: %s\n", examenes[i].fecha);

    }

}



int main(){

    int opcion;


    do{

        printf("\n========================");
        printf("\n AGENDA ESTUDIANTIL");
        printf("\n========================");

        printf("\n1. Registrar materia");
        printf("\n2. Mostrar materias");
        printf("\n3. Registrar tarea");
        printf("\n4. Mostrar tareas");
        printf("\n5. Registrar examen");
        printf("\n6. Mostrar examenes");
        printf("\n7. Salir");

        printf("\nSeleccione opcion: ");
        scanf("%d",&opcion);



        switch(opcion){

            case 1:
                registrarMateria();
                break;

            case 2:
                mostrarMaterias();
                break;

            case 3:
                registrarTarea();
                break;

            case 4:
                mostrarTareas();
                break;

            case 5:
                registrarExamen();
                break;

            case 6:
                mostrarExamenes();
                break;

            case 7:
                printf("Programa finalizado\n");
                break;


            default:
                printf("Opcion incorrecta\n");
        }


    }while(opcion!=7);



    return 0;
}