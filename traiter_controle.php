<?php 
session_start(); 

/*ini_set('display_errors', TRUE);
ini_set('display_startup_errors', TRUE);*/


if (!file_exists('config.php')) {
   header('Location:install1.php');	
		} 

//require_once "signgate_common.php";
//include_once "config.php";
//require_once "ai_error.php";
require_once('../pdf/fpdf/fpdf.php');
				require_once('../pdf/fpdi/fpdi.php');
				require_once('../phpqrcode/qrlib.php');

require_once "inc/signgate_common.php";
require_once "inc/ai_error.php";

if(file_exists("./DB_Functions.php"))
		require_once './DB_Functions.php';
		else if(file_exists("../DB_Functions.php"))
		require_once '../DB_Functions.php';


//Verify document signature from Android request
//$_POST['androidSignature']="M2KmfCVntIo6drrwvySU/upCmH0NFnue9MMfPQLYyjcbz/TcjKvdnObUp1kFgwCH6jGpIMU1eRTxg112owijWsM5k9T1n1IURY5h9qoTv2cuZ1LGDF16YAidnhTjDZkY0Zg4vZlqxA76CWU87eAHGOPTbGZGYbAA2INdXhQi+2TVSMAlo9F9/rR66ghgVQHLjB0XZdHmsiN0XP6HjIkPLfcwciZC45QqByH8ysKiRT1FS3T73IGpRpBlduBbBlLDtOVnmkYGms6yeq9HsfB5p273pKhdXFxgaiRdfqAfxQOLQUiSF1cM6qlo+YO0AEIC5FcFitgDf7CVhNQHFXALhQ==DM20220323021954974522";

if( isset($_POST['androidSignature']) ){
		
		$androidSignature = $_POST['androidSignature'];
 
		//Use substr to extract document number and his signature
		$documentNumber = substr($androidSignature,344);

		$androidSignature = substr($androidSignature ,0 ,344);

		$functions = new DB_Functions();	

		$resultat = $functions->Get_Document_Infos($documentNumber);
 

		$strSignCert = $resultat['strSignCert'];
		$hashDocument = $resultat['hash'];


		$verify_sign = ai_verify_sha2withrsa($strSignCert, $aiCertUSAGE_SIGN, base64_encode($hashDocument), $androidSignature);
	
		if($verify_sign==$RET_OK)
		  {    
			 echo "Document valide et authentique";  exit;
			 
	    }else{
												
				 echo "Document Invalide "; exit;
		 }

} else { 


	



  $DATE_ID = "";
  $MODELE_ID = "";
  $DESC_ID = "";
  $DOC_ID="";
  $NUMERO_ID="";
  $TYPE_ID="";
  $SIGN_NOM_ID="";
  
  

	$strCHALLENGE = md5(uniqid(rand(), true));
	//Get data from client.
	$strSignedData		= trimNewLine($_POST["UserSignValue"]);
	$strSignCert		= $_POST["UserSignCert"];
	$strEncSessionKey	= trimNewLine($_POST["EncryptedSessionKeyForServer"]);
	$strEncRandomValue	= $_POST["EncryptedUserRandomNumber"];
	/*$strEncPassword		= $_POST["EncryptedLoginPassword"];
	$strEncUserSSN	= $_POST["EncryptedUserSSN"];	
	$strEncLoginID		= $_POST["EncryptedLoginID"];*/	
	$strEncryptedData	= $_POST["EncryptedData"];

	$documentSignature	= trimNewLine($_POST["documentSignature"]); 


	//$file	= $_POST["EncrypFile"];
	
	//echo $strEncryptedPrenomValue;
	
	$strDecryptSessionKeyForServer = ai_asy_rsa_decrypt($aiKmPriKey, $aiKmCertKey, $aiKeyPasswd, $strEncSessionKey);
    //echo( "DecryptSessionKeyForServer : [".$strDecryptSessionKeyForServer."] <br>");


	//세션키전문 파싱(IV, SymKey, alg)
	$secretKey = getSymKeyInfo($strDecryptSessionKeyForServer);
	$aiIV = $secretKey["iv"];
	$strDecryptSessionKeyForServer = $secretKey["symkey"];

	//S-4. Decrypt (Login ID & Password) with Session Key
	$DecryptedData= ai_sya_seed_decrypt($strEncryptedData, $strDecryptSessionKeyForServer, $aiIV );
	$v23=base64_decode($DecryptedData);
	$myArray = explode('@', $v23);
	
	 $DATE_ID = $myArray[0];
	 $DESC_ID = $myArray[1];
     $MODELE_ID = $myArray[2];
     //$DOC_ID = $myArray[3];
	 $NUMERO_ID = $myArray[4];
	 $TYPE_ID=$myArray[5];
	 $SIGN_NOM_ID=$myArray[6];
	 $OBSERVA_ID=$myArray[7];
	 $REMAK_ID=$myArray[8];

	 $hashDocuments = $myArray[9];  





	 /*if ($DOC_ID=='') {
		 
		 echo ("<script language='JavaScript'>
			window.alert('Aucun document PDF trouvé !')
			window.location.href='lister_demande.php';
			</script>"); 			
	  
     }  */
	
	/*echo "strEncDate -----------:".$strEncDate."<br>";
	echo "------------------------------------------------------------------------<br>";
	echo "strEncDocument -----------:".$strEncDocument."<br>";
	echo "------------------------------------------------------------------------<br>";
	echo $strEncDesc."<br>";
	echo "------------------------------------------------------------------------<br>";*/
	
	$strOriginalMessage =$v23;
	$TrimstrSignCert = trimNewLine(trimCERTHeadLine($strSignCert));
	$verify_sign = ai_verify_sha2withrsa($strSignCert, $aiCertUSAGE_SIGN, base64_encode($strOriginalMessage), $strSignedData);

	 

	
	
	if($verify_sign==$RET_OK)
	{
		//echo "Digital Signature is valid => signature data : [$strOriginalMessage]<br>";

	}else{
	
		echo "<script>alert(\"Digital Signature is not valid ==>".$ai_pki_error_mesg[$verify_sign].$verify_sign."\");history.back();</script>";
		//exit;
	}


    //=================================================================
	// certificate information
	//=================================================================
	$arCertInfo = ai_getcertinfo($strSignCert,$aiCertTYPE_PEM);
	//print_r($arCertInfo);
	if(!is_array($arCertInfo)){
		$bCheckFlag = false;
		echo "Error Code : ".$arClientData."<br>";
		echo "Error Mesg : ".$ai_pki_error_mesg[$arSignMesgVerify]." <br>";
		//exit;
	}
	//S-7. Check allowed subscriber's certificate policy
	
	// Allowed Certificate Policy List
	$allowedPolicyOIDs = array(
		"2 16 120 20001 4 1 1 2 4",   // test
		"2 16 120 200001 4 1 1 2 4",   // test
		"2 16 120 200001 4 1 1 2 1",   // RAAdmin
		"2 16 120 200001 4 1 1 1 2",   // Server
		"2 16 120 200001 4 1 1 2 2",   // CorpPrivate
		"2 16 120 200001 4 1 1 1 3",   // CorpPublic	
		"2 16 120 200001 4 1 1 2 1",   // Individual
		"2 16 120 200001 4 1 1 1 1"    // Administration
	);
	
	
	$isOid = false;
	if(!in_array($arCertInfo["CERTPOLICYID"], $allowedPolicyOIDs)){
		echo "<script>alert(\"Your Certificate is not allowed to access our service. oid:'". $arCertInfo["CERTPOLICYID"]. "'\");history.back();</script>";
		return;
	}
	//

	
	//S-6. Check validity of subscriber's certificate

	$validate_cert	= ai_validate_cert($strSignCert, $aiCertTYPE_PEM, $aiCertUSAGE_SIGN, $aiTrustedCert);
	
	//"cn=TEST POLICY 091117,ou=PKI Center,ou=ANTIC RA,ou=GovRA,o=ANTIC CA,c=CM"; //
	$dn=$arCertInfo["SUBJECTNAME"];
		
	/*if($validate_cert==$RET_OK)
	{
		//echo "To check Validity==>".				"Good<br>";
	}else{   
		echo "<script>alert(\"certificate is not valid  'Invalidity=>". $ai_pki_error_mesg[$validate_cert]. "'\"); </script>";
	//	exit;
	}
	*/
	 
	//S-9. Check subscriber's certificate(DN and serial number) is match with registered in database 
	
	//$dbDN = "cn=minpostel,ou=PKI Center,ou=ANTIC RA,ou=GovRA,o=ANTIC CA,c=CM";
	
	/***********************************************************************************************************************
	*
	* DEBUT DU PROCESSUS D'ENREGISTREMENT DU QRCODE SIGNE SUR LE DOCUMENT PDF.
	*
	**********************************************************************************************************************/
	
	      //$data = $conn->query("select * from template  where idtemplate='$modele'");
		  
		  if($_SESSION['login_type']=="Directeur") 
					{   
						$liste="lister_demande";
					}
					else if($_SESSION['login_type']=="Collaborateur") 
					 {  
						$liste="lister";
					 }	
		  $db2 = new DB_Functions();	
		  $result22 = $db2->Get_DN_USER($dn,$_SESSION['login']);	   
		  $users_dn = $result22['users_dn'];
		  
		  if($users_dn=="") {
			$ramdom = md5(uniqid(rand(), true));
			header('Location:accueil.php?param=traiter&id='.$NUMERO_ID.'&id2=1&menu=menu_demande&error_certificate='.$ramdom);
			exit();
		  }		  
		  else if($TYPE_ID=="rejeter"){
			  
			  $db = new DB_Functions();	
			  $datas = $db->Update_Demande_statut($NUMERO_ID,"3",$_SESSION['login'],$OBSERVA_ID);	
			  
			    $myArray = explode('##', $REMAK_ID);		
				$result = $db->List_Document_ID($NUMERO_ID);				
				$asn=0;
				foreach($result as $rs1){
										//$code_doc=$rs1['document_id'];
					$datas = $db->Update_Document_Remarque($rs1['document_id'],$myArray[$asn]);	
					$asn=$asn+1;
				}
			  
			  $ramdom = md5(uniqid(rand(), true));
				header('Location:accueil.php?param='.$liste.'&menu=menu_demande&succes='.$ramdom);
			  
		  }
		  else {
					  
		  $db = new DB_Functions();	
		  $result2 = $db->Get_TemplateID($MODELE_ID);	   
		  $positionx = $result2['tmpl_positionx'];
		  $positiony =$result2['tmpl_positiony'];
		   $signxx =$result2['tmpl_signxx'];
		    $signyy =$result2['tmpl_signyy'];
		  $dimxy = $result2['tmpl_dimxy'];
		   $signxy = $result2['tmpl_signxy'];
		  $orientation =$result2['tmpl_orientation'];
		  $format = $result2['tmpl_format'];
		  $nbpage = $result2['tmpl_nbpage'];
		  $pagex = $result2['tmpl_pagex'];
		  
		  if( $signxy>0 && !file_exists("../signature/".$SIGN_NOM_ID."")){
			$ramdom = md5(uniqid(rand(), true));
			header('Location:accueil.php?param=traiter&id='.$NUMERO_ID.'&id2=1&menu=menu_demande&error_sign_file='.$ramdom);
			exit();
			}
		  
					if($orientation=='Paysage'){
						$type='L';
						$type_page='295';
					}
					else if ($orientation=='Portrait')
					{
						$type='P';
						$type_page='210';
					}
					
			 
			 $kz = $db-> Count_Demand_Distinct($NUMERO_ID);  
			if ($kz['total']>0) {	  
				$pk = $db->List_DemandeFrom_Numero($NUMERO_ID);
				
				//Si c'est plusieurs document
				$myArray = explode('##', $REMAK_ID);						
				$asn=0;	
				//Parcours des différents documents de la demande	
				$serverName="localhost";
				$dbusername="root";
				$dbpassword="@Cncce@2022";
				$dbname="dcs_client";

				
				$conn = new mysqli($serverName, $dbusername, $dbpassword, $dbname);	

				$result = mysqli_query($conn,"SELECT * FROM dcs_demande, dcs_document WHERE dcs_demande.demande_numero='$NUMERO_ID' AND dcs_document.document_numero='$NUMERO_ID' 
				                          ORDER BY dcs_document.document_id DESC");
											 
							 
				//foreach($pk as $rs){
				while($rs = mysqli_fetch_array($result)) {

					 					//$op=$row['operateur'];  
										$DOC_ID=$rs['document_nom'];
										$DOC_CODE=$rs['document_code'];
										
										if( !file_exists("../demandePDF/".$DOC_ID."")){
											$ramdom = md5(uniqid(rand(), true));
											header('Location:accueil.php?param=traiter&id='.$NUMERO_ID.'&id2=1&menu=menu_demande&error_pdf_doc='.$ramdom);
											exit();
										}
											
										$query2=$db->Count_Row_DocSigned();				
										$row_count = $query2['doc_id'];
										
										if($row_count>0){
										$code = $query2['doc_id'];
										$code =$code +1;
										}
										else {
										  $code=1;
										}	

										//$ramdon12 ="DCS".date('YmdHis'); // $db->randomKey(22);
										$ramdon12 ="DCS".date('YmdHis').preg_replace("/^.*\./i","", microtime(true));
										$code=$ramdon12.$code;
										
										  $db = new DB_Functions();	
										  $login=$_SESSION['login'];
										  $rws = $db->Get_Identification();
										  $param_ip=$rws['param_ip'];
										  $param_port=$rws['param_port'];



										  //Save document signature
										  //But before that, we need to verify the signature first
										  	$verify_sign = ai_verify_sha2withrsa($strSignCert, $aiCertUSAGE_SIGN, base64_encode($hashDocuments), $documentSignature);
	
												if($verify_sign==$RET_OK)
												{    
													//echo "Digital Signature is valid => signature data : [$hashDocuments]<br>"; exit;
													$documentID=$NUMERO_ID;
 										            $db->Save_Document_Signature($documentSignature,$documentID);

 										            //Update document table with User's signing certificate
 										            $db->Save_UserSign_Certificate($strSignCert,$documentID);  

//Update document table with Document ID
 										            $db->Save_DocID($documentID,$code); 

												}else{
												
													echo "<script>alert(\"Digital Signature of the document is not valid ==>".$ai_pki_error_mesg[$verify_sign].$verify_sign."\");history.back();</script>";
														//exit;
													}
					 					  



							
											//$hash=md5($strSignedData);
												$userdn=$arCertInfo["SUBJECTNAME"];
												$serialnumber=$arCertInfo["SERIALNUM"];
												//$codeqr_22= $code_structure.'&'.$userdn.'&'.$serialnumber.'&'.$code.'&'.$hash;
												$hash =sha1_file('../demandePDF/'.$DOC_ID);
												//$param_ip="192.168.5.3";
												//$param_port="80";
												$codeqr_22="ANTIC&".$param_ip.'&'.$param_port.'&'.$code.'&'.$hash;

													$pdf = new FPDI();  
																				
													//$mention="Assez-Bien";
													$faitle=date('Y-m-d');
													
													//$fullPathToPDF = '/usr/local/common/my.pdf';
													$pageCount = $pdf->setSourceFile('../demandePDF/'.$DOC_ID);   
													
													for ($i = 1; $i <= $pageCount; $i++) {
														$tplIdx = $pdf->importPage($i);
														$pdf->AddPage($type,$format); 
														$pdf->useTemplate($tplIdx, 1, 1, $type_page);
														
														if($pagex==$i) {
															
															$pdf->SetFont('Arial','I',15);
															$pdf->SetTextColor(194,8,8);
															if($orientation=="Paysage") {															
															$pdf->SetXY(120, 120); //sets the position for the name	
															$pdf->Cell(288,16,$myArray[$asn]);	
															}else {
															$pdf->SetXY(120, 120); //sets the position for the name	
															$pdf->Cell(288,16,$myArray[$asn]);	
															}															
															$asn=$asn+1;
															
															//chiffrement des données dans le code QR
															/*$encrypt_key = "tIC@cPki237&doc@A123apps";
															$data = $db->Encrypt_Data($codeqr_22,$encrypt_key);*/


															//Add signature in QR Code
															$data = $documentSignature.$code ;
															  
																QRcode::png($data,'../qr/'.$code.'.png',QR_ECLEVEL_M,2,1);
																//$pdf->Image('2015.png',$positionx,$positiony,$dimxy);
																$pdf->Image('../qr/'.$code.'.png',$positionx,$positiony,$dimxy); 
																
																if($signxy>0) {
																$pdf->Image('../signature/'.$SIGN_NOM_ID,$signxx,$signyy,$signxy);	
																}
														}
													}							
													
													$login = $_SESSION['login'];
													//$location = $dir.'/'; 
													$location = '../pdf/';
													$pdf->Output($location.$code.'.pdf','F');
													
							$datas = $db->Save_SignDocs($faitle,$DESC_ID,$DOC_ID,$MODELE_ID,$userdn,
							$serialnumber,$strSignedData,'',$_SESSION['login'],$code,$DOC_CODE,$SIGN_NOM_ID);	
							/*$datas = $db->Save_SignDocs($faitle,$DESC_ID,$DOC_ID,$MODELE_ID,$userdn,
							$serialnumber,$documentSignature,'',$_SESSION['login'],$code,$DOC_CODE,$SIGN_NOM_ID); */					
					}

						mysqli_close($conn);
			}
			
		$datas = $db->Update_Demande_statut($NUMERO_ID,"2",$_SESSION['login'],$OBSERVA_ID);	
		$myArray = explode('##', $REMAK_ID);
		
				$result = $db->List_Document_ID($NUMERO_ID);				
				$asn=0;
				foreach($result as $rs1){
										//$code_doc=$rs1['document_id'];
					$datas = $db->Update_Document_Remarque($rs1['document_id'],$myArray[$asn]);	
					$asn=$asn+1;
				}
		
					
			    $ramdom = md5(uniqid(rand(), true));
				header('Location:accueil.php?param='.$liste.'&menu=menu_demande&succes='.$ramdom);
		  }	

} //End First IF
		  
?>
