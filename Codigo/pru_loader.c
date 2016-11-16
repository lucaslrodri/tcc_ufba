/* Carregando as bibliotecas */
#include <prussdrv.h>
#include <pruss_intc_mapping.h> 
#define PRU_NUM 	0 /*Define que ser� gravado no 1o n�cleo*/
   
void main (void){
    /* Cria a estrutura de dados que representa a PRU com o nome pruss_intc_initdata   */
	/* Essa estrutura de dados ser�o utilizadas nas fun��es como prussdrv_init */
    /* PRUSS_INTC_INITDATA � uma constante de pruss_intc_mapping.h */
    tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_INITDATA;
	
    /* Inicializa o PRU e aloca a mem�ria */
    prussdrv_init ();		
    prussdrv_open (PRU_EVTOUT_0);
       
    /* Mapeia as interrup��es do PRU */
    prussdrv_pruintc_init(&pruss_intc_initdata);
       
    /* Carrega e executa o programa no PRU */
    prussdrv_exec_program (PRU_NUM, "./PRU_ADC.bin");
       
    /* Espera a rotina ser executada */
    prussdrv_pru_wait_event (PRU_EVTOUT_0);  // Isso assume que houve uma interrup��o 
   
    /* Desativa a PRU e fecha o mapa de mem�ria */
    prussdrv_pru_disable(PRU_NUM); 
    prussdrv_exit ();
}