library(tidyverse)



# Lab workstation
#setwd('D:/Jojo/PhD/ClimbingRobot/ClimbingLizardDLCAnalysis/all_geckos-jojo-hemi-2020-03-19/analysis-results')
# Jojo Laptop - all geckos
setwd('C:/Users/JojoS/Documents/phd/ClimbingRobot_XGen4/ClimbingLizardDLCAnalysis/gecko_all-jojo-hemi-2020-03-18/analysis-results')
# Jojo Laptop - debug geckos
setwd('C:/Users/JojoS/Documents/phd/ClimbingRobot_XGen4/ClimbingLizardDLCAnalysis/geckos-jojo-hemi-2020-02-17/analysis-results')

setwd('H:/DLCs/Gecko01-Tasmin-Gecko-2020-04-16/analysis-results')
setwd('H:/DLCs/Gecko02-Tasmin-Geckos-2020-04-14/analysis-results')
setwd('H:/DLCs/Gecko03-Tasmin-Gecko-2020-04-15/analysis-results')




filenames <- (Sys.glob("*resnet50_Gecko*.csv"))
filenames <- (Sys.glob("*resnet50*.csv"))  

stride_name=NA 
phase=c(5,6) #which columns to call for each phase
df_out<-data.frame(name=NA,ID=NA,speed=NA,stepphase=NA,direction=NA,foot=NA,body_angle=NA,
                   step_length_F=NA,step_length_H=NA,
                   midwrist_F=NA,midwrist_H=NA,
                   limbROM_F=NA,limbROM_H=NA,
                   spineROM_F=NA, spineROM_H=NA, 
                   CROM_F=NA, CROM_H=NA, diag=NA, 
                   Sum_toe_F=NA, Mean_toe_F=NA, Sum_toe_H=NA, Mean_toe_H=NA)



for (ii in 1:length(filenames)){
  #ii=1
  dat<-read.csv(filenames[ii])
  
  
  
  for (ll in 1:2){
    #ll = 1 - 1 = FR, 2 = FL
    #jj = 1
    stride_name=NA 
    #get the number of strides for the footphase
    for (jj in 1:nrow(dat)){
      stride_name[jj]=str_split(tail(str_split(dat[,phase[ll]],"'")[[jj]],n=2)[1],'00')[[1]][2]
    }
    
    
    
    if (phase[ll]=="6") {
      foot_phase='FR'
      
      
      #nn=1 - for debugging
      for (nn in 1:length(unique(stride_name))){
        
        dat_temp=dat[which(stride_name==unique(stride_name)[nn]),]
        dat_temp<-dat_temp[!grepl("stride", dat_temp$stepphase_FR),]
        #head(test1)
        #dat_temp$stepphase_FL
        
        diag=dat_temp$mid_stance_wrist_angles_mean_FR+dat_temp$mid_stance_wrist_angles_mean_HL
        
        Sum_toe_FR=mean(rowSums(dat_temp[,45:48], na.rm=T), na.rm=T)
        Mean_toe_FR=mean(as.matrix(dat_temp[,45:48]), na.rm=T)
        
        Sum_toe_HL=mean(rowSums(dat_temp[,53:56], na.rm=T), na.rm=T)
        Mean_toe_HL=mean(as.matrix(dat_temp[,53:56]), na.rm=T)
        
        midwrist_FR=mean(dat_temp$mid_stance_wrist_angles_mean_FR, na.rm=T)
        midwrist_HL=mean(dat_temp$mid_stance_wrist_angles_mean_HL, na.rm=T)
        
        step_length_FR=mean(dat_temp$step.length_FR, na.rm=T)
        step_length_HL=mean(dat_temp$step.length_HL, na.rm=T)
        
        limbROM_FR=mean(dat_temp$limbROM_FR, na.rm=T)
        limbROM_HL=mean(dat_temp$limbROM_HL, na.rm=T)
        
        spineROM_FR=mean(dat_temp$spineROM_FR, na.rm=T)
        spineROM_HL=mean(dat_temp$spineROM_HL, na.rm=T)
        
        CROM_FR=mean(dat_temp$CROM_FR, na.rm=T)
        CROM_HL=mean(dat_temp$CROM_HL, na.rm=T)
        
        df_temp<-data.frame(name=filenames[ii],
                            ID=str_split(filenames[ii],'_')[[1]][1],
                            speed=mean(dat_temp$speed_PXperS, na.rm=T),
                            stepphase=nn,
                            direction=dat_temp$direction_of_climbing[1][1],
                            foot=foot_phase,
                            body_angle=mean(dat_temp$body_deflection_angle, na.rm=T),
                            step_length_F=step_length_FR,
                            step_length_H=step_length_HL,
                            midwrist_F=midwrist_FR,
                            midwrist_H=midwrist_HL,
                            limbROM_F=limbROM_FR,
                            limbROM_H=limbROM_HL,
                            spineROM_F=spineROM_FR,
                            spineROM_H=spineROM_HL,
                            CROM_F=CROM_FR, 
                            CROM_H=CROM_HL, 
                            diag=mean(diag, na.rm=T),
                            Sum_toe_F=Sum_toe_FR,
                            Mean_toe_F=Mean_toe_FR,
                            Sum_toe_H=Sum_toe_HL,
                            Mean_toe_H=Mean_toe_HL)
        
        df_out<-rbind(df_out,df_temp)
        
      }# ends nn loop
      
    }else
    {
      foot_phase='FL'
      #nn=2 - for debugging
      for (nn in 1:length(unique(stride_name))){
        
        dat_temp=dat[which(stride_name==unique(stride_name)[nn]),]
        dat_temp<-dat_temp[!grepl("stride", dat_temp$stepphase_FR),]
        #dat_temp$stepphase_FL
        
        diag=dat_temp$mid_stance_wrist_angles_mean_FL+dat_temp$mid_stance_wrist_angles_mean_HR
        Sum_toe_FL=mean(rowSums(dat_temp[,41:44], na.rm=T), na.rm=T)
        Mean_toe_FL=mean(as.matrix(dat_temp[,41:44]), na.rm=T)
        
        Sum_toe_HR=mean(rowSums(dat_temp[,49:52], na.rm=T), na.rm=T)
        Mean_toe_HR=mean(as.matrix(dat_temp[,49:52]), na.rm=T)
        
        midwrist_FL=mean(dat_temp$mid_stance_wrist_angles_mean_FL, na.rm=T)
        midwrist_HR=mean(dat_temp$mid_stance_wrist_angles_mean_HR, na.rm=T)
        
        step_length_FL=mean(dat_temp$step.length_FL, na.rm=T)
        step_length_HR=mean(dat_temp$step.length_HR, na.rm=T)
        
        limbROM_FL=mean(dat_temp$limbROM_FL, na.rm=T)
        limbROM_HR=mean(dat_temp$limbROM_HR, na.rm=T)
        
        spineROM_FL=mean(dat_temp$spineROM_FL, na.rm=T)
        spineROM_HR=mean(dat_temp$spineROM_HR, na.rm=T)
        
        CROM_FL=mean(dat_temp$CROM_FL, na.rm=T)
        CROM_HR=mean(dat_temp$CROM_HR, na.rm=T)
        
        df_temp<-data.frame(name=filenames[ii],
                            ID=str_split(filenames[ii],'_')[[1]][1],
                            speed=mean(dat_temp$speed_PXperS, na.rm=T),
                            stepphase=nn,
                            direction=dat_temp$direction_of_climbing[1][1],
                            foot=foot_phase,
                            body_angle=mean(dat_temp$body_deflection_angle, na.rm=T),
                            step_length_F=step_length_FL,
                            step_length_H=step_length_HR,
                            midwrist_F=midwrist_FL,
                            midwrist_H=midwrist_HR,
                            limbROM_F=limbROM_FL,
                            limbROM_H=limbROM_HR,
                            spineROM_F=spineROM_FL,
                            spineROM_H=spineROM_HR,
                            CROM_F=CROM_FL, 
                            CROM_H=CROM_HR,
                            diag=mean(diag, na.rm=T),
                            Sum_toe_F=Sum_toe_FL,
                            Mean_toe_F=Mean_toe_FL,
                            Sum_toe_H=Sum_toe_HR,
                            Mean_toe_H=Mean_toe_HR)
                            
        
        df_out<-rbind(df_out,df_temp)
        
      } # end nn lopp
      
    } #end else condition
    
    
  }#end ll loop
}

df_out<-df_out[-1,]
write.csv(df_out, 'gecko_03-22-04-20.csv')
head(df_out)
