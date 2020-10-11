<?php

$servidor = 'http://localhost/procesamenu';

//Devuelve la lista de platos obtenida desde el servidor $server
function getPlatos(){
  global $servidor;
  $res = json_decode(  file_get_contents("$servidor".'/platos'), true);
  return $res;
}

//Devuelve la lista de platos y la lista de ingredientes
function getAll($entrada){
  global $servidor;
  $parametro='['.$entrada[0].','.$entrada[1].','.$entrada[2].','.$entrada[3].','.$entrada[4].
                         ','.$entrada[5].','.$entrada[6].','.$entrada[7].','.$entrada[8].','.$entrada[9].
                         ','.$entrada[10].','.$entrada[11].','.$entrada[12].','.$entrada[13].']';
  $res = json_decode(  file_get_contents("$servidor".'/all?v='.$parametro), true);
  return $res;
}

//Obtiene del servidor una predicci�n en base a los datos de entrada
function getPrediccion($entrada){
  global $servidor;
  $parametro='['.$entrada[0].','.$entrada[1].','.$entrada[2].','.$entrada[3].','.$entrada[4].','.$entrada[5].','.$entrada[6].','.$entrada[7].','.$entrada[8].','.$entrada[9].','.$entrada[10].','.$entrada[11].','.$entrada[12].','.$entrada[13].']';
  $res = json_decode(  file_get_contents("$servidor".'/prediccion?v='.$parametro), true);
  return $res;
}

//Muestra el menu final y los ingredientes
function showAll($platos, $platosSel, $ingredientes){
  $cabecera='
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Men� semanal</title>
        <link href="style.css" rel="stylesheet" type="text/css">
    </head>
    <h1>Men� semanal</h1>
    <table name="tabla">
        <col span="1" style="background-color: lightgrey">
        <thead>
           <tr>
                <th>D�a de la semana</th>
                <th>Comida</th>
                <th>Cena</th>
            </tr>
        </thead>
    ';
  $cola='
    </table>
    </body>
    </html>
    ';
  echo $cabecera;
  echo '<tr><td>Lunes</td><td>'.$platos[$platosSel[0]-1][1].'</td><td>'.$platos[$platosSel[1]-1][1].'</td></tr>';
  echo '<tr><td>Martes</td><td>'.$platos[$platosSel[2]-1][1].'</td><td>'.$platos[$platosSel[3]-1][1].'</td></tr>';
  echo '<tr><td>Mi�rcoles</td><td>'.$platos[$platosSel[4]-1][1].'</td><td>'.$platos[$platosSel[5]-1][1].'</td></tr>';
  echo '<tr><td>Jueves</td><td>'.$platos[$platosSel[6]-1][1].'</td><td>'.$platos[$platosSel[7]-1][1].'</td></tr>';
  echo '<tr><td>Viernes</td><td>'.$platos[$platosSel[8]-1][1].'</td><td>'.$platos[$platosSel[9]-1][1].'</td></tr>';
  echo '<tr><td>S�bado</td><td>'.$platos[$platosSel[10]-1][1].'</td><td>'.$platos[$platosSel[11]-1][1].'</td></tr>';
  echo '<tr><td>Domingo</td><td>'.$platos[$platosSel[12]-1][1].'</td><td>'.$platos[$platosSel[13]-1][1].'</td></tr>';
  $intermedio='
    </table><br><br>
    <h2>Lista de la compra</h2>
    <ul>
    ';
  //Y los ingredientes
  for($i=0;$i<(sizeof($ingredientes)-1);$i+=2)
    $intermedio=$intermedio.'<li>'.$ingredientes[$i+1].'&nbsp;&nbsp;'.$ingredientes[$i].'</li>';
  $intermedio=$intermedio.'</ul>';
  echo $intermedio;
  echo $cola;
}

//Muestra una fila de comidas y cenas para el d�a indicado y con el listado de platos propuesto
//En caso de que haya predicciones, se selecciona la opci�n predicha
function printSelect($dia,$platos,$prediccionComida = NULL,$prediccionCena = NULL){
  $opcionesComida='<option value="0">-----------------------</option>';
  $opcionesCena='<option value="0">-----------------------</option>';
  foreach($platos as $id => $plato){
    if(isset($prediccionComida) && ($plato[0] == $prediccionComida))
      $opcionesComida=$opcionesComida.'<option value="'.$plato[0].'" selected="selected">'.$plato[1].'</option>';
    else
      $opcionesComida=$opcionesComida.'<option value="'.$plato[0].'">'.$plato[1].'</option>';
    if(isset($prediccionCena) && ($plato[0] == $prediccionCena))
      $opcionesCena=$opcionesCena.'<option value="'.$plato[0].'" selected="selected">'.$plato[1].'</option>';
    else
      $opcionesCena=$opcionesCena.'<option value="'.$plato[0].'">'.$plato[1].'</option>';
  }
  $res='
    <tr>
        <td>'.$dia.'</td>
        <td>
            <select class="buscador" id="'.$dia.'Comida" name="'.$dia.'Comida" onchange="enviar_formularioSelect(&quot;'.$dia.'Comida&quot;)" style="display:inline; width:90%;">
            '.$opcionesComida.'
            </select>
            <input type="checkbox" id="cb'.$dia.'Comida" name="cb'.$dia.'Comida" style="display: inline;" onclick="toggleCheckBox(&quot;'.$dia.'Comida&quot;)">
        </td>
        <td>
            <select class="buscador" id="'.$dia.'Cena" name="'.$dia.'Cena" onchange="enviar_formularioSelect(&quot;'.$dia.'Cena&quot;)" style="display:inline; width:90%;">
            '.$opcionesCena.'
            </select>
            <input type="checkbox" id="cb'.$dia.'Cena" name="cb'.$dia.'Cena" style="display: inline;" onclick="toggleCheckBox(&quot;'.$dia.'Cena&quot;)">
        </td>
    </tr>
  ';
  return $res;
}

//Muestra por pantalla la tabla de platos, inicialmente vac�a
//Puede recibir la predicci�n de los men�s a poner as� como los platos que ha marcado el usuario
function showTable($platos, $prediccion = NULL, $marcados = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]){
  $cabecera='
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="ISO-8859-15">
        <title>Menu semanal</title>
        <link href="style.css" rel="stylesheet" type="text/css">
        <link href="select2/select2.min.css" rel="stylesheet" />
        <script src="select2/jquery.min.js"></script>
        <script src="select2/select2.min.js"></script>
        <script>
          $(document).ready(function() {
            $(".buscador").select2();
            $(".buscador").on("change", function (e) {
              enviar_formularioSelect(e.target.getAttribute("name"));
            });
          });
        </script>

    <script>
    function enviar_formularioSelect(campo){
       if(document.getElementById(campo).value==0)
         document.getElementById(campo+"User").value=-1;
       else
        document.getElementById(campo+"User").value=document.getElementById(campo).
        value;
      document.formulario1.submit();
    }

    //Genera nueva predicci�n aunque no se haya seleccionado un plato
    //Esto se supone que es �til cuando marcas varios checkboxes y quieres
    //que afine la predicci�n con el resto.
    function enviar_formulario(){
       document.formulario1.submit();
    }

    //Tras pulsar un checkbox, si se selecciona, se marcar� el valor en parametro hidden correspondiente
    //Si se deselecciona, se pondr� un cero en el par�metro hidden correspondiente.
    function toggleCheckBox(campo){
       if (document.getElementById("cb"+campo).checked)
         document.getElementById(campo+"User").value=document.getElementById(campo).value;
       else
         document.getElementById(campo+"User").value="0";
    }

    //Establece los CheckBox seg�n el par�metro de entrada
    function setCheckBoxes(marcados){
      var dias=["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"];
      for(var i=0; i<7 ;i++){
          var id="cb"+dias[i]+"Comida";
          if(marcados[i*2]!=0){
            document.getElementById(id).checked = true;
          }else
            document.getElementById(id).checked = false;
          id="cb"+dias[i]+"Cena";
          if(marcados[i*2+1]!=0)
            document.getElementById(id).checked = true;
          else
            document.getElementById(id).checked = false;
      }
    }

    //Da por v�lido todo el men�. En este caso tendr�as que mostrar la pantalla de imprimirlo,
    //generar la lista de ingredientes, quitar los checkboxes. Haz volar tu imaginaci�n.
    function validate(){
        document.getElementById("FIN").value="true";
        enviar_formulario();
    }

    //Resetea la tabla
    function resetAll(){
        //He de marcar todas las select a valor cero
        //He de marcar todos los hidden a valor cero
        //He de desmarcar todos los checkbox
        var dias=["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"];
        for(var i=0; i<7 ;i++){
            //Select
            document.getElementById(dias[i]+"Comida").value="0";
            document.getElementById(dias[i]+"Cena").value="0";
            //Hidden
            document.getElementById(dias[i]+"ComidaUser").value="0";
            document.getElementById(dias[i]+"CenaUser").value="0";
            //CheckBox
            document.getElementById("cb"+dias[i]+"Comida").checked = false;
            document.getElementById("cb"+dias[i]+"Cena").checked = false;
        }
    }

    </script>

    </head>
    <body onload="setCheckBoxes(['.implode(',', $marcados).'])">
    <h1>Menu semanal</h1>
    <form action="http://proyectosraspiadv.hopto.org/menu.php" method="post" name="formulario1">
    <table name="tabla">
        <col span="1" style="background-color: lightgrey"></col>
        <thead>
            <tr>
                <th>Dia de la semana</th>
                <th>Comida</th>
                <th>Cena</th>
            </tr>
        </thead>
    ';
  $cola='
    </table>
    <ul class="botones">
        <li class="bckColorBoton" onclick="resetAll()">Resetear tabla</li>
        <li class="bckColorBoton" onclick="enviar_formulario()">Nueva prediccion</li>
        <li class="bckColorBoton" onclick="validate()">Validar menu</li>
    </ul>
    <input type="hidden" id="LunesComidaUser" name="LunesComidaUser" value="'.$marcados[0].'">
    <input type="hidden" id="LunesCenaUser" name="LunesCenaUser" value="'.$marcados[1].'">
    <input type="hidden" id="MartesComidaUser" name="MartesComidaUser" value="'.$marcados[2].'">
    <input type="hidden" id="MartesCenaUser" name="MartesCenaUser" value="'.$marcados[3].'">
    <input type="hidden" id="MiercolesComidaUser" name="MiercolesComidaUser" value="'.$marcados[4].'">
    <input type="hidden" id="MiercolesCenaUser" name="MiercolesCenaUser" value="'.$marcados[5].'">
    <input type="hidden" id="JuevesComidaUser" name="JuevesComidaUser" value="'.$marcados[6].'">
    <input type="hidden" id="JuevesCenaUser" name="JuevesCenaUser" value="'.$marcados[7].'">
    <input type="hidden" id="ViernesComidaUser" name="ViernesComidaUser" value="'.$marcados[8].'">
    <input type="hidden" id="ViernesCenaUser" name="ViernesCenaUser" value="'.$marcados[9].'">
    <input type="hidden" id="SabadoComidaUser" name="SabadoComidaUser" value="'.$marcados[10].'">
    <input type="hidden" id="SabadoCenaUser" name="SabadoCenaUser" value="'.$marcados[11].'">
    <input type="hidden" id="DomingoComidaUser" name="DomingoComidaUser" value="'.$marcados[12].'">
    <input type="hidden" id="DomingoCenaUser" name="DomingoCenaUser" value="'.$marcados[13].'">
    <input type="hidden" id="FIN" name="FIN" value="false">
    </form>
    </body>
    </html>
    ';
  echo $cabecera;
  if($prediccion==NULL){
    echo printSelect("Lunes",$platos);
    echo printSelect("Martes",$platos);
    echo printSelect("Miercoles",$platos);
    echo printSelect("Jueves",$platos);
    echo printSelect("Viernes",$platos);
    echo printSelect("Sabado",$platos);
    echo printSelect("Domingo",$platos);
  }else{
    echo printSelect("Lunes",$platos,$prediccion[0],$prediccion[1]);
    echo printSelect("Martes",$platos,$prediccion[2],$prediccion[3]);
    echo printSelect("Miercoles",$platos,$prediccion[4],$prediccion[5]);
    echo printSelect("Jueves",$platos,$prediccion[6],$prediccion[7]);
    echo printSelect("Viernes",$platos,$prediccion[8],$prediccion[9]);
    echo printSelect("Sabado",$platos,$prediccion[10],$prediccion[11]);
    echo printSelect("Domingo",$platos,$prediccion[12],$prediccion[13]);
  }
  echo $cola;
}


//Cuando el usuario marque una opci�n, se envia al servidor los valores de los hidden (seleccionados por el usuario)
//Se a�ade la funcionalidad de validar en funci�n del par�metro FIN, con lo que se discrimina su hemos de pedir
//una nueva predicci�n o la lista de ingredientes.

$platos=getPlatos();
if(isset($_POST['FIN']) && ($_POST['FIN']=="true")){
  $definidos[0]=$_POST["LunesComidaUser"];
  $definidos[1]=$_POST["LunesCenaUser"];
  $definidos[2]=$_POST["MartesComidaUser"];
  $definidos[3]=$_POST["MartesCenaUser"];
  $definidos[4]=$_POST["MiercolesComidaUser"];
  $definidos[5]=$_POST["MiercolesCenaUser"];
  $definidos[6]=$_POST["JuevesComidaUser"];
  $definidos[7]=$_POST["JuevesCenaUser"];
  $definidos[8]=$_POST["ViernesComidaUser"];
  $definidos[9]=$_POST["ViernesCenaUser"];
  $definidos[10]=$_POST["SabadoComidaUser"];
  $definidos[11]=$_POST["SabadoCenaUser"];
  $definidos[12]=$_POST["DomingoComidaUser"];
  $definidos[13]=$_POST["DomingoCenaUser"];
  $all=getAll($definidos);
  showAll($platos,$all[0],$all[1]);
}else{
  if(isset($_POST['LunesComida'])){
    $definidos[0]=$_POST["LunesComidaUser"];
    $definidos[1]=$_POST["LunesCenaUser"];
    $definidos[2]=$_POST["MartesComidaUser"];
    $definidos[3]=$_POST["MartesCenaUser"];
    $definidos[4]=$_POST["MiercolesComidaUser"];
    $definidos[5]=$_POST["MiercolesCenaUser"];
    $definidos[6]=$_POST["JuevesComidaUser"];
    $definidos[7]=$_POST["JuevesCenaUser"];
    $definidos[8]=$_POST["ViernesComidaUser"];
    $definidos[9]=$_POST["ViernesCenaUser"];
    $definidos[10]=$_POST["SabadoComidaUser"];
    $definidos[11]=$_POST["SabadoCenaUser"];
    $definidos[12]=$_POST["DomingoComidaUser"];
    $definidos[13]=$_POST["DomingoCenaUser"];
    $prediccion=getPrediccion($definidos);
    showTable($platos,$prediccion[0],$prediccion[1]);
  }
  else{
    showTable($platos);
  }
}
?>

