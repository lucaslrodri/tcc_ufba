/* Carregando as bibliotecas */
#include <prussdrv.h>
#include <pruss_intc_mapping.h> 
#define PRU_NUM 	0 /*Define que será gravado no 1o núcleo*/
   
void main (void){
    /* Cria a estrutura de dados que representa a PRU com o nome pruss_intc_initdata   */
	/* Essa estrutura de dados serão utilizadas nas funções como prussdrv_init */
    /* PRUSS_INTC_INITDATA é uma constante de pruss_intc_mapping.h */
    tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_INITDATA;
	
    /* Inicializa o PRU e aloca a memória */
    prussdrv_init ();		
    prussdrv_open (PRU_EVTOUT_0);
       
    /* Mapeia as interrupções do PRU */
    prussdrv_pruintc_init(&pruss_intc_initdata);
       
    /* Carrega e executa o programa no PRU */
    prussdrv_exec_program (PRU_NUM, "./PRU_ADC.bin");
       
    /* Espera a rotina ser executada */
    prussdrv_pru_wait_event (PRU_EVTOUT_0);  // Isso assume que houve uma interrupção 
   
    /* Desativa a PRU e fecha o mapa de memória */
    prussdrv_pru_disable(PRU_NUM); 
    prussdrv_exit ();
}